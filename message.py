class Message:
    """SMS or MMS message.

    Model that describes a message.
    """
    sender_gaia_id = None  # This seems to be the ID to use
    sender_chat_id = None  # Not used
    timestamp = None
    medium_type = None  # Not used
    event_type = None  # Not used
    content = None  # Message body
    attachments = None  # MMS attachments

    def __init__(self, sender_gaia_id=None, sender_chat_id=None, timestamp=None,
                 medium_type=None, event_type=None, content=None, attachments=None):
        self.sender_gaia_id = sender_gaia_id
        self.sender_chat_id = sender_chat_id
        self.timestamp = timestamp
        self.medium_type = medium_type
        self.event_type = event_type
        self.content = content
        self.attachments = attachments
