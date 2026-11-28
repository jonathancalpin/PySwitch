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

from ...misc import PeriodCounter, get_current_millis
from . import ampz_raw_bytes, ampz_frame, AMPZ_PREFIX, TYPE_HELLO_REPLY, TYPE_HELLO_REQUEST, LINK


class AmpzProtocol:

    # settle_millis: how long the link must be quiet after an error before asking for a dump.
    # min_rerequest_millis: never ask more often than this while errors keep coming.
    def __init__(self, retry_millis = 3000, period_counter = None, settle_millis = 400,
                 min_rerequest_millis = 1000, now = None):
        self.alive = False
        self.debug = False   # set by BidirectionalClient
        self.retry_period = period_counter if period_counter else PeriodCounter(retry_millis)
        self.__midi = None
        self.__client = None
        self.__now = now if now else get_current_millis
        self.__settle_millis = settle_millis
        self.__min_rerequest_millis = min_rerequest_millis
        self.__errors_seen = LINK.errors
        self.__last_error_at = 0
        self.__last_request_at = 0

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
        if not self.alive:
            if self.retry_period.exceeded:
                self.__request()
            return
        # Something was lost on the way in: ask for everything again once the burst is over.
        now = self.__now()
        if LINK.errors != self.__errors_seen:
            self.__errors_seen = LINK.errors
            self.__last_error_at = now
            self.__pending = True
        if getattr(self, "_AmpzProtocol__pending", False) \
                and now - self.__last_error_at >= self.__settle_millis \
                and now - self.__last_request_at >= self.__min_rerequest_millis:
            self.__pending = False
            self.__request()

    def __request(self):
        self.__last_request_at = self.__now()
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
