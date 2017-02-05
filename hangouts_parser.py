import json
from argparse import Namespace
from participant import Participant
from message import Message
from conversation import Conversation
from attachment import Attachment


class HangoutsParser:
    """Parses the Google Takeout JSON export for Hangouts SMS/MMS messages."""

    def parse_input_file(self, hangouts_file_name, user_phone_number):
        """Parse the Hangouts JSON file containing SMS/MMS messages.

        :param hangouts_file_name: filename of the Hangouts messages
        :param user_phone_number: phone number of the user (some messages are missing this)
        :return: list of Conversation objects, GAIA ID of the user
        """
        conversations = []
        self_gaia_id = None  # gaia_id for the phone owner
        with open(hangouts_file_name, 'r') as data_file:
            # Read the Hangouts JSON file and turn into objects
            data = json.load(data_file, object_hook=lambda d: Namespace(**d))
            # Iterate through each conversation in the list
            for conversation_state in data.conversation_state:
                # Get the nested conversation_state
                state = getattr(conversation_state, "conversation_state", None)
                if state is not None:
                    # Get the conversation object
                    conversation = getattr(state, "conversation", None)
                    if conversation is None:
                        continue
                    # Create a new conversation and store its properties
                    current_conversation = Conversation()
                    current_conversation.network_types = getattr(conversation, "network_type", None)
                    self_conversation_state = getattr(conversation, "self_conversation_state", None)
                    if self_conversation_state is not None:
                        current_conversation.active_timestamp = self._try_int_attribute(self_conversation_state,
                                                                                       "active_timestamp")
                        self_read_state = getattr(self_conversation_state, "self_read_state", None)
                        if self_read_state is not None:
                            current_conversation.self_latest_read_timestamp = \
                                self._try_int_attribute(self_read_state, "latest_read_timestamp")
                            participant_id = getattr(self_read_state, "participant_id", None)
                            if participant_id is not None:
                                current_self_gaia_id = self._try_int_attribute(participant_id, "gaia_id")
                                if current_self_gaia_id is not None:
                                    self_gaia_id = current_self_gaia_id
                    # Get the conversation participants
                    participant_data = getattr(conversation, "participant_data", None)
                    read_state = getattr(conversation, "read_state", None)
                    if participant_data is not None:
                        current_conversation.participants = self._extract_participants(conversation.participant_data,
                                                                                       read_state, user_phone_number,
                                                                                       self_gaia_id)
                    # Get the conversation messages
                    events = getattr(state, "event", None)
                    if events is not None:
                        current_conversation.messages = self._process_messages(events)
                    conversations.append(current_conversation)
        return conversations, self_gaia_id

    def _extract_participants(self, participant_data, read_state, user_phone_number, self_gaia_id):
        # Builds a dictionary of the participants in a conversation/thread
        participant_list = {}
        for participant in participant_data:
            # Create a new participant and store its properties
            current_participant = Participant()
            current_participant.name = getattr(participant, "fallback_name", None)
            participant_id = getattr(participant, "id", None)
            current_participant.chat_id = self._try_int_attribute(participant_id, "chat_id")
            current_participant.gaia_id = self._try_int_attribute(participant_id, "gaia_id")
            current_participant.type = getattr(participant, "participant_type", None)
            # Parse participant phone details
            phone_number = getattr(participant, "phone_number", None)
            if phone_number is not None:
                current_participant.e164_number = getattr(phone_number, "e164", None)
                i18n_data = getattr(phone_number, "i18n_data", None)
                if i18n_data is not None:
                    current_participant.country_code = getattr(i18n_data, "country_code", None)
                    current_participant.international_number = getattr(i18n_data, "international_number", None)
                    current_participant.national_number = getattr(i18n_data, "national_number", None)
                    current_participant.region_code = getattr(i18n_data, "region_code", None)
            # Sometimes the phone number is missing...
            # This only seems to happen for the user, not others
            if (current_participant.gaia_id is not None
                and current_participant.gaia_id == self_gaia_id
                and (current_participant.e164_number is None
                     and current_participant.international_number is None
                     and current_participant.national_number is None)):
                current_participant.e164_number = user_phone_number
                current_participant.international_number = user_phone_number
            participant_list[current_participant.gaia_id] = current_participant
        # Parse read_state to get latest_read_timestamp for each participant
        if read_state is not None:
            for participant_read_state in read_state:
                participant_id = getattr(participant_read_state, "participant_id", None)
                gaia_id = self._try_int_attribute(participant_id, "gaia_id")
                latest_read_timestamp = self._try_int_attribute(participant_read_state, "latest_read_timestamp")
                if gaia_id in participant_list.keys():
                    participant_list[gaia_id].latest_read_timestamp = latest_read_timestamp
        return participant_list

    def _process_messages(self, events):
        # Parses events/messages in a conversation
        message_list = []
        for event in events:
            # Create new message and store its properties
            current_message = Message()
            sender_id = getattr(event, "sender_id", None)
            current_message.sender_gaia_id = self._try_int_attribute(sender_id, "gaia_id")
            current_message.sender_chat_id = self._try_int_attribute(sender_id, "chat_id")
            current_message.timestamp = self._try_int_attribute(event, "timestamp")
            delivery_medium = getattr(event, "delivery_medium", None)
            if delivery_medium is not None:
                current_message.medium_type = getattr(delivery_medium, "medium_type", None)
            current_message.event_type = getattr(event, "event_type", None)
            # Parse message chat content
            chat_message = getattr(event, "chat_message", None)
            if chat_message is not None:
                message_content = getattr(chat_message, "message_content", None)
                if message_content is not None:
                    if hasattr(message_content, "segment"):
                        current_message.content = self._process_message_content(message_content.segment)
                    if hasattr(message_content, "attachment"):
                        current_message.attachments = self._process_message_attachments(message_content.attachment)
            message_list.append(current_message)
        return message_list

    @staticmethod
    def _process_message_content(segment_list):
        # Parse the content/body of a message
        message_content = ""
        for current_segment in segment_list:
            if hasattr(current_segment, "formatting"):
                # TODO: FORMATTING tag handling
                # formatting
                #    bold = boolean
                #    italics = boolean
                #    strikethrough = boolean
                #    underline = boolean
                pass
            if hasattr(current_segment, "type"):
                if hasattr(current_segment, "text"):
                    message_content += current_segment.text

                if current_segment.type == "TEXT":
                    pass
                elif current_segment.type == "LINE_BREAK":
                    pass
                elif current_segment.type == "LINK":
                    # TODO: LINK type handling
                    # link_data
                    #    display_url = string
                    #    link_target = string
                    pass
                else:
                    print("Error: Unknown message content TYPE: " + current_segment.type)
                    continue
            else:
                print("Error: Message content missing TYPE!")
                continue
        return message_content

    def _process_message_attachments(self, attachment_list):
        # Parse the attachments of an MMS message
        attachments = []
        for current_attachment in attachment_list:
            embed_item = getattr(current_attachment, "embed_item", None)
            if embed_item is not None:
                plus_photo = getattr(embed_item, "embeds.PlusPhoto.plus_photo", None)
                if plus_photo is not None:
                    current_attachment = Attachment()
                    current_attachment.album_id = self._try_int_attribute(plus_photo, "album_id")
                    current_attachment.photo_id = self._try_int_attribute(plus_photo, "photo_id")
                    current_attachment.media_type = getattr(plus_photo, "media_type", None)
                    current_attachment.original_content_url = getattr(plus_photo, "original_content_url", None)
                    current_attachment.download_url = getattr(plus_photo, "download_url", None)
                    attachments.append(current_attachment)
        return attachments

    @staticmethod
    def _try_int_attribute(obj, attribute_name):
        # Return the integer value in the object with the specified name
        # If it cannot be cast as an int, return whatever it actually is
        result = None
        if obj is not None and attribute_name is not None:
            temp_attr = getattr(obj, attribute_name, None)
            if temp_attr is not None:
                try:
                    result = int(temp_attr)
                except ValueError:
                    result = temp_attr
        return result
