##############################################################################
#
# Repairs Ampz traffic arriving through a Bluetooth-to-DIN adapter.
#
# Observed on the MIDI IN jack (serial console capture, 2026-11-27): CCs and Program Changes
# arrive intact, but two SysEx frames out of three lose their leading F0 and gain a stray
# Bluetooth timestamp byte (0x80..0xFF) after their F7. The frame's data bytes are all still
# there. Every Ampz frame starts with the same four bytes after F0 (7D 41 7A 01), and that
# signature never occurs inside a CC or PC, so the stream can be put back together:
#
#   - the signature seen outside a frame gets its F0 back
#   - a signature seen inside an unterminated frame closes that frame first
#   - any byte >= 0x80 that is not F0, F7, a CC or a PC status is dropped (leaked timestamp,
#     stray F7, realtime)
#   - a CC or PC status immediately followed by the signature was a leaked byte, not a status
#
# Wraps the UART for adafruit_midi: only read() is used by the library.
#
##############################################################################

from . import AMPZ_PREFIX


class SysExRepairInput:

    def __init__(self, port, prefix = AMPZ_PREFIX):
        self.__port = port
        self.__prefix = bytes(prefix)
        self.__in_frame = False
        self.__cand = bytearray()      # data bytes that may be the start of a signature
        self.__cand_start = 0          # frame offset where the candidate began
        self.__frame_pos = 0           # data bytes seen since the frame's F0
        self.__held = bytearray()      # a CC/PC status with its data so far

    @property
    def in_waiting(self):
        return getattr(self.__port, "in_waiting", 0)

    def read(self, nbytes = None):
        raw = self.__port.read(nbytes)
        if not raw:
            return None
        out = bytearray()
        for b in raw:
            self.__feed(b, out)
        return bytes(out) if out else None

    # One byte of the wire stream; appends repaired bytes to out.
    def __feed(self, b, out):
        plen = len(self.__prefix)

        # Inside a CC/PC: collect data, but a signature or a stray byte unmasks a leaked status.
        if self.__held:
            if b < 0x80:
                self.__held.append(b)
                need = 3 if self.__held[0] < 0xC0 else 2
                if len(self.__held) < need:
                    return
                data = bytes(self.__held[1:])
                if data == self.__prefix[:len(data)]:
                    # Looks like the start of a frame: the status was a leaked byte.
                    self.__held = bytearray()
                    for d in data:
                        self.__feed(d, out)
                    return
                out += self.__held
                self.__held = bytearray()
                return
            # A status byte before the message was complete: the held one was noise.
            self.__held = bytearray()
            # fall through with b

        if self.__in_frame:
            if b == 0xF7:
                self.__flush_cand(out)
                out.append(0xF7)
                self.__in_frame = False
                return
            if b == 0xF0:
                self.__flush_cand(out)
                out.append(0xF7)                 # close the frame that lost its end
                out.append(0xF0)
                self.__frame_pos = 0
                return
            if b >= 0x80:
                return                           # leaked timestamp inside the frame
            # Data: a signature later in the frame means the previous F7 and the next F0 both
            # went missing. At offset 0 it is simply this frame's own prefix.
            if not self.__cand:
                self.__cand_start = self.__frame_pos
            self.__cand.append(b)
            self.__frame_pos += 1
            if bytes(self.__cand) == self.__prefix[:len(self.__cand)]:
                if len(self.__cand) == plen:
                    if self.__cand_start > 0:
                        out.append(0xF7)
                        out.append(0xF0)
                        self.__frame_pos = plen
                    out += self.__cand
                    self.__cand = bytearray()
                return
            self.__flush_cand(out)
            return

        # Outside a frame
        if b == 0xF0:
            self.__drop_cand()
            out.append(0xF0)
            self.__in_frame = True
            self.__frame_pos = 0
            return
        if 0xB0 <= b <= 0xCF:
            self.__drop_cand()
            self.__held = bytearray([b])
            return
        if b >= 0x80:
            self.__drop_cand()
            return                               # stray F7, realtime, leaked timestamp
        # Data outside any message: only meaningful as the start of a frame that lost its F0.
        self.__cand.append(b)
        if bytes(self.__cand) == self.__prefix[:len(self.__cand)]:
            if len(self.__cand) == plen:
                out.append(0xF0)
                out += self.__cand
                self.__cand = bytearray()
                self.__in_frame = True
                self.__frame_pos = plen
            return
        # Not a signature: drop the oldest byte and re-test the rest, which may start one.
        rest = bytes(self.__cand[1:])
        self.__cand = bytearray()
        for d in rest:
            self.__feed(d, out)

    # Candidate bytes inside a frame were ordinary data after all.
    def __flush_cand(self, out):
        if self.__cand:
            out += self.__cand
            self.__cand = bytearray()

    def __drop_cand(self):
        self.__cand = bytearray()
