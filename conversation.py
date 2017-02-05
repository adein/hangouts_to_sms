class Conversation:
    """SMS or MMS conversation.

    Model that describes a thread of SMS or MMS messages and participants.
    """
    network_types = None  # SMS/MMS seem to use PHONE
    active_timestamp = None  # Not used
    self_latest_read_timestamp = None  # Not used
    participants = None
    messages = None

    def __init__(self, network_types=None, participants=None, active_timestamp=None,
                 self_read_timestamp=None, messages=None):
        self.network_types = network_types
        self.active_timestamp = active_timestamp
        self.self_latest_read_timestamp = self_read_timestamp
        self.participants = participants
        self.messages = messages
