##############################################################################
#
# Ampz client: feedback from the Ampz iOS amp app.
#
# Ampz echoes every stomp, looper and scene CC with the true state (0 off, 64 half, 127 on)
# and carries names and colours in a short SysEx frame:
#
#     F0 7D 41 7A 01 <type> <index> 00 <payload> F7
#
# 0x7D is the MIDI non-commercial manufacturer ID. The frame is parsed here by byte position
# on the reassembled message (manufacturer bytes and data joined), so it does not matter how
# the MIDI library splits a one-byte manufacturer ID from the data.
#
##############################################################################

from ...controller.client import ClientParameterMapping
from adafruit_midi.system_exclusive import SystemExclusive

AMPZ_PREFIX = (0x7D, 0x41, 0x7A, 0x01)

TYPE_STOMP_LABEL = 0x01      # index = stomp 0..9; payload = colour byte, then ASCII name
TYPE_PRESET_NAME = 0x03      # index 0; payload = ASCII name
TYPE_HELLO_REPLY = 0x7E      # index 0; payload 00 01 (Ampz is alive, sent at the start of every dump)
TYPE_HELLO_REQUEST = 0x7F    # index 0; payload 00 00 (Captain -> Ampz: please send a dump)

# Colour byte -> RGB. Mirrors Ampz's effect families.
FAMILY_COLORS = {
    0: (50, 50, 50),       # none (empty stomp): default label colour, LED off
    1: (0, 90, 255),       # dynamics
    2: (255, 125, 0),      # drive
    3: (255, 0, 0),        # amplifier
    4: (180, 0, 120),      # modulation
    5: (0, 255, 0),        # pitch
    6: (255, 255, 0),      # filter
    7: (0, 200, 255),      # wah
    8: (0, 150, 130),      # reverb
    9: (100, 255, 160),    # delay
    10: (140, 80, 20),     # cabinets
    11: (190, 190, 190),   # utility
}


# Builds an Ampz frame as a SystemExclusive message (without F0/F7, the library adds them).
def ampz_frame(type, index, payload):
    return SystemExclusive(
        manufacturer_id = [AMPZ_PREFIX[0]],
        data = [AMPZ_PREFIX[1], AMPZ_PREFIX[2], AMPZ_PREFIX[3], type, index, 0x00] + list(payload)
    )


# Returns the whole message body (manufacturer bytes plus data) as a list, with one trailing
# 0xF7 or 0x00 removed if the MIDI library left it on. None if the message is not SysEx.
def ampz_raw_bytes(midi_message):
    if not isinstance(midi_message, SystemExclusive):
        return None
    raw = list(midi_message.manufacturer_id) + list(midi_message.data)
    if raw and (raw[-1] == 0xF7 or raw[-1] == 0x00):
        raw = raw[:-1]
    return raw


# Response-only mapping for one Ampz frame (type and index). Values:
#   TYPE_STOMP_LABEL  -> (colour, name)
#   TYPE_PRESET_NAME  -> name
#   anything else     -> numeric payload (msb * 128 + lsb), e.g. 1 for the hello reply
class AmpzSysexMapping(ClientParameterMapping):

    def __init__(self, name, type, index):
        super().__init__(
            name = name,
            create_key = ClientParameterMapping,
            response = ampz_frame(type, index, [])
        )
        self.frame_type = type
        self.frame_index = index

    def parse_against(self, midi_message, response):
        raw = ampz_raw_bytes(midi_message)
        if raw is None or len(raw) < 7:
            return None
        if tuple(raw[0:4]) != AMPZ_PREFIX:
            return None
        if raw[4] != self.frame_type or raw[5] != self.frame_index:
            return None

        payload = raw[7:]

        if self.frame_type == TYPE_STOMP_LABEL:
            if not payload:
                return (0, "")
            return (payload[0], _ascii(payload[1:]))

        if self.frame_type == TYPE_PRESET_NAME:
            return _ascii(payload)

        if len(payload) >= 2:
            return payload[-2] * 128 + payload[-1]
        if len(payload) == 1:
            return payload[0]
        return 0


def _ascii(bytes_list):
    return ''.join(chr(int(c)) for c in bytes_list)
