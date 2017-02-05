class Participant:
    """Participant in a conversation.

    Model that describes a person in a conversation.
    """
    name = None
    gaia_id = None
    chat_id = None  # Not used
    type = None  # Not used
    e164_number = None
    country_code = None  # Not used
    international_number = None
    national_number = None
    region_code = None  # Not used
    latest_read_timestamp = None  # Not used

    def __init__(self, name=None, gaia_id=None, chat_id=None, type=None, e164_number=None, country_code=None,
                 international_number=None, national_number=None, region_code=None, latest_timestamp=None):
        self.name = name
        self.gaia_id = gaia_id
        self.chat_id = chat_id
        self.type = type
        self.e164_number = e164_number
        self.country_code = country_code
        self.international_number = international_number
        self.national_number = national_number
        self.region_code = region_code
        self.latest_read_timestamp = latest_timestamp
