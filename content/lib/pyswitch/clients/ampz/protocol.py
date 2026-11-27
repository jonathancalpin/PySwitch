##############################################################################
#
# Ampz "protocol" object for communication.py.
#
# PySwitch's BidirectionalClient hands unparsed messages and a periodic update() to this
# object. Ampz pushes its state on its own (every change, plus a full dump on connect, preset
# load and app start), so nothing here is polled. The one job is the hello: until Ampz has
# answered once, ask it for a dump every few seconds, so a Captain powered on after the app
# gets its labels without anyone touching the phone.
#
##############################################################################

from ...misc import PeriodCounter
from . import ampz_raw_bytes, ampz_frame, AMPZ_PREFIX, TYPE_HELLO_REPLY, TYPE_HELLO_REQUEST


class AmpzProtocol:

    def __init__(self, retry_millis = 3000, period_counter = None):
        self.alive = False
        self.debug = False   # set by BidirectionalClient
        self.retry_period = period_counter if period_counter else PeriodCounter(retry_millis)
        self.__midi = None
        self.__client = None

    # Called before usage, with a midi handler.
    def init(self, midi, client):
        self.__midi = midi
        self.__client = client

    # Ampz pushes every value; no mapping is handled bidirectionally.
    def is_bidirectional(self, mapping):
        return False

    # Never feed a set value back locally: the LED follows Ampz's echo, not the press.
    def feedback_value(self, mapping):
        return False

    def get_color(self):
        return (0, 255, 0) if self.alive else (255, 0, 0)

    # Ask for a dump until Ampz answers. A real PeriodCounter starts exceeded, so the first
    # update() after boot sends at once.
    def update(self):
        if self.alive:
            return
        if self.retry_period.exceeded:
            self.__midi.send(ampz_frame(TYPE_HELLO_REQUEST, 0, [0x00, 0x00]))

    # Consumes the Ampz hello reply; everything else is left to others.
    def receive(self, midi_message):
        raw = ampz_raw_bytes(midi_message)
        if raw is None or len(raw) < 5:
            return False
        if tuple(raw[0:4]) != AMPZ_PREFIX:
            return False
        if raw[4] == TYPE_HELLO_REPLY:
            self.alive = True
            return True
        return False
