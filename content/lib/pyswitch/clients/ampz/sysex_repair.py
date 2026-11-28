##############################################################################
#
# Repairs Ampz traffic arriving through a Bluetooth-to-DIN adapter.
#
# Observed on the MIDI IN jack (raw UART captures, 2026-11-27):
#
#   - consecutive CCs arrive with running status (the status byte is sent once and then left
#     out), which adafruit_midi does not understand, so every CC after the first was lost
#   - Bluetooth timestamp bytes (0x80..0xFF) leak into the stream: between messages, between
#     a CC's number and its value, and inside SysEx frames
#   - two SysEx frames in three lose their leading F0 (the data bytes are all still there)
#   - now and then a frame loses data bytes (caught by the frame's length byte, see __init__)
#
# Ampz only ever sends CCs, Program Changes and its own SysEx frames, and every Ampz frame
# starts with the same four bytes after F0 (7D 41 7A 01), a signature that never occurs
# inside a CC or PC. So the stream can be put back together:
#
#   - running status is expanded: data bytes after a CC or PC get that status again
#   - the signature seen outside a frame gets its F0 back; inside an unterminated frame it
#     closes that frame first
#   - a byte >= 0x80 that is not F0, F7, a CC or a PC status is dropped wherever it sits; one
#     inside a half-received CC or PC is ignored rather than aborting the message
#   - a CC or PC status immediately followed by the signature was a leaked byte, not a status
#   - Ampz sends one PC at a time, so data continuing after a PC means a leaked byte sat
#     where a CC burst's status should have been: the run is delivered as CCs
#   - data bytes that belong to nothing (no running status, no signature) are information
#     lost and counted on LINK so the protocol asks Ampz for a fresh dump
#   - only whole messages are handed on: adafruit_midi discards a SysEx that is not complete
#     within one read, and a 31250-baud link delivers most frames in several reads
#
# Wraps the UART for adafruit_midi: only read() is used by the library.
#
##############################################################################

from . import AMPZ_PREFIX, LINK


class SysExRepairInput:

    def __init__(self, port, prefix = AMPZ_PREFIX, log_raw = False):
        self.__port = port
        self.__log_raw = log_raw
        self.__prefix = bytes(prefix)
        self.__in_frame = False
        self.__cand = bytearray()      # data bytes that may be the start of a signature
        self.__cand_start = 0          # frame offset where the candidate began
        self.__frame_pos = 0           # data bytes seen since the frame's F0
        self.__held = bytearray()      # a CC/PC status with its data so far
        self.__running = None          # last CC/PC status, for running status
        self.__frame = bytearray()     # the frame being received, from its F0, released at F7
        self.__pending_pc = None       # a complete PC, held one byte to see whether data follows

    @property
    def in_waiting(self):
        return getattr(self.__port, "in_waiting", 0)

    def read(self, nbytes = None):
        raw = self.__port.read(nbytes)
        if not raw:
            if self.__pending_pc:
                pc = self.__pending_pc                # nothing followed it: a real PC
                self.__pending_pc = None
                return bytes(pc)
            return None
        if self.__log_raw:   # pragma: no cover
            print("RAW " + " ".join("%02x" % b for b in raw))
        out = bytearray()
        for b in raw:
            self.__feed(b, out)
        return bytes(out) if out else None

    # One byte of the wire stream; appends repaired bytes to out.
    def __feed(self, b, out):
        if self.__pending_pc:
            pc = self.__pending_pc
            self.__pending_pc = None
            if b < 0x80:
                # Data after a PC: the PC status was a leaked byte in place of a CC burst's B0.
                self.__running = 0xB0 | (pc[0] & 0x0F)
                self.__held = bytearray([self.__running, pc[1]])
                self.__feed_held(b, out, True)
                return
            out += pc
        if self.__held:
            self.__feed_held(b, out, True)
        elif self.__in_frame:
            self.__feed_in_frame(b, out)
        else:
            self.__feed_outside(b, out)

    # Inside a CC/PC whose status we have. check_prefix: whether completed data that looks
    # like the start of an Ampz signature is handed on as one (off while re-feeding bytes
    # that already failed that test, so they cannot loop).
    def __feed_held(self, b, out, check_prefix):
        if b == 0xF0:
            # A frame starts before the message was complete: its rest is gone.
            self.__held = bytearray()
            LINK.lost()
            self.__feed_outside(b, out)
            return
        if b >= 0x80:
            return                                   # leaked byte mid-message: ignore it
        self.__held.append(b)
        need = 3 if self.__held[0] < 0xC0 else 2
        if len(self.__held) < need:
            return
        data = bytes(self.__held[1:])
        self.__held = bytearray()
        if check_prefix and data == self.__prefix[:len(data)]:
            # Looks like the start of a frame whose F0 was eaten; the status was a leaked
            # byte or running status that does not apply. Carry on as a signature candidate.
            self.__cand = bytearray(data)
            self.__cand_start = 0
            return
        if need == 2:
            self.__pending_pc = bytes([self.__running]) + data
            return
        out.append(self.__running)
        out += data

    # Inside a SysEx frame.
    def __feed_in_frame(self, b, out):
        plen = len(self.__prefix)
        frame = self.__frame
        if b == 0xF7:
            self.__flush_cand(frame)
            frame.append(0xF7)
            out += frame                             # whole frame: release it
            self.__frame = bytearray()
            self.__in_frame = False
            return
        if b == 0xF0:
            self.__flush_cand(frame)
            frame.append(0xF7)                       # close the frame that lost its end
            out += frame
            self.__frame = bytearray([0xF0])
            self.__frame_pos = 0
            return
        if b >= 0x80:
            return                                   # leaked byte inside the frame
        # Data: a signature later in the frame means the previous F7 and the next F0 both
        # went missing. At offset 0 it is simply this frame's own prefix.
        if not self.__cand:
            self.__cand_start = self.__frame_pos
        self.__cand.append(b)
        self.__frame_pos += 1
        if bytes(self.__cand) == self.__prefix[:len(self.__cand)]:
            if len(self.__cand) == plen:
                if self.__cand_start > 0:
                    frame.append(0xF7)
                    out += frame
                    frame = self.__frame = bytearray([0xF0])
                    self.__frame_pos = plen
                frame += self.__cand
                self.__cand = bytearray()
            return
        self.__flush_cand(frame)

    # Between messages.
    def __feed_outside(self, b, out):
        plen = len(self.__prefix)
        if b == 0xF0:
            self.__drop_cand()
            self.__frame = bytearray([0xF0])
            self.__in_frame = True
            self.__frame_pos = 0
            self.__running = None                    # SysEx cancels running status
            return
        if 0xB0 <= b <= 0xCF:
            self.__drop_cand()
            self.__running = b
            self.__held = bytearray([b])
            return
        if b >= 0x80:
            self.__drop_cand()
            return                                   # stray F7, realtime, leaked timestamp
        # A data byte. An open signature candidate takes it first; otherwise it is running
        # status data when a CC/PC status is known, or the possible start of a frame that
        # lost its F0.
        if not self.__cand and self.__running is not None:
            self.__held = bytearray([self.__running])
            self.__feed_held(b, out, True)
            return
        self.__cand.append(b)
        if bytes(self.__cand) == self.__prefix[:len(self.__cand)]:
            if len(self.__cand) == plen:
                self.__frame = bytearray([0xF0]) + self.__cand
                self.__cand = bytearray()
                self.__in_frame = True
                self.__frame_pos = plen
                self.__running = None
            return
        # Not a signature after all.
        rest = bytes(self.__cand)
        self.__cand = bytearray()
        if self.__running is not None:
            # Running-status data that happened to start like the signature: deliver it as
            # CC/PC data, without re-testing the same bytes for a signature.
            for d in rest:
                if self.__held:
                    self.__feed_held(d, out, False)
                elif self.__in_frame:
                    self.__feed_in_frame(d, out)
                else:
                    self.__held = bytearray([self.__running])
                    self.__feed_held(d, out, False)
            return
        # No status to belong to: a CC that lost its status, or a frame that lost its start
        # and its signature. Information lost; the oldest byte goes, the rest are re-tested.
        LINK.lost()
        for d in rest[1:]:
            self.__feed(d, out)

    # Candidate bytes inside a frame were ordinary data after all.
    def __flush_cand(self, target):
        if self.__cand:
            target += self.__cand
            self.__cand = bytearray()

    # Candidate bytes outside a frame, cut short by a status: with no running status to
    # explain them they were information lost.
    def __drop_cand(self):
        if self.__cand and self.__running is None:
            LINK.lost()
        self.__cand = bytearray()
