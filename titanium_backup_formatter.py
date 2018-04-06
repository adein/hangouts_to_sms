import urllib.request
import base64
import uuid
import os
from datetime import datetime
from xml.sax.saxutils import escape


# XML output constants for Titanium Backup
SMS_OUTPUT_HEADER_1 = "<?xml version=\'1.0\' encoding=\'UTF-8\' standalone=\'yes\' ?>"
SMS_OUTPUT_HEADER_2 = "<threads count=\"{}\" xmlns=\"http://www.titaniumtrack.com/ns/titanium-backup/messages\">"
MMS_PART = "<part contentType=\"{}\" order=\"{}\" name=\"part-0\" encoding=\"{}\">{}</part>"


class TitaniumBackupFormatter:
    """Converts parsed Hangouts SMS/MMS messages from HangoutsParser for use with Titanium Backup"""

    def create_output_file(self, conversations, self_gaia_id, output_file_name):
        """Creates an XML file containing SMS/MMS that can be used in Titanium Backup.

        :param conversations: list of Conversation objects
        :param self_gaia_id: GAIA ID of the user
        :param output_file_name: name of the output XML file
        :return:
        """
        try:
            os.remove(output_file_name)
        except OSError:
            pass
        with open(output_file_name, 'w') as sms_output:
            sms_output.write(SMS_OUTPUT_HEADER_1)
            sms_output.write(SMS_OUTPUT_HEADER_2.format(len(conversations)))
            for conversation in conversations:
                # Skip non-SMS conversations
                if "PHONE" not in conversation.network_types:
                    continue
                sms_output.write("<thread address=\"{}\">".format(
                    self._create_participant_string(conversation.participants, self_gaia_id)))
                for message in conversation.messages:
                    if message.sender_gaia_id is None:
                        print("Error: message sender gaia ID is None!")
                        continue
                    if message.sender_gaia_id not in conversation.participants.keys():
                        print("Error: could not match sender gaia ID to participant IDs!")
                        continue
                    is_sms = len(conversation.participants) <= 2 and message.attachments is None
                    is_sent = message.sender_gaia_id == self_gaia_id
                    message_timestamp = self._timestamp_to_utc_string(message.timestamp)
                    if is_sms:
                        # Store the other participant in the SMS conversation
                        non_self_participant = None
                        for participant in conversation.participants.values():
                            if participant.gaia_id != self_gaia_id:
                                non_self_participant = participant
                                break
                        # start of sms
                        message_string = "<sms msgBox=\"{}\"".format("sent" if is_sent else "inbox")
                        # 'sent' messages only have 'date' field
                        # 'inbox' messages have 'date' and 'dateSent' fields
                        message_string += " date=\"{}\"".format(message_timestamp)
                        if not is_sent:
                            message_string += " dateSent=\"{}\"".format(message_timestamp)
                        # always assume 'locked' = false
                        message_string += " locked=\"false\""

                        # TODO: seen
                        # TODO: read
                        message_string += " seen=\"false\" read=\"true\""

                        # address is always the number of the other person in an SMS conversation
                        message_string += " address=\"{}\"".format(
                            self._get_participant_phone_number(non_self_participant))
                        # plain or base64
                        content_is_plain = self._is_ascii(message.content)
                        # content
                        if message.content is not None:
                            message_string += " encoding=\"{}\"".format("plain" if content_is_plain else "base64")
                        message_string += ">{}".format(
                            escape(message.content) if content_is_plain
                            else self._base64_text(message.content))
                        message_string += "</sms>"
                        sms_output.write(message_string)
                    else:
                        # start of mms
                        message_string = "<mms msgBox=\"{}\" version=\"1.2\"".format("sent" if is_sent else "inbox")
                        # type
                        message_string += " type=\"{}\"".format("sendReq" if is_sent else "retrieveConf")
                        # content type is fixed..?
                        message_string += " contentType=\"application/vnd.wap.multipart.related\""
                        # 'sent' messages only have 'date' field
                        # 'inbox' messages have 'date' and 'dateSent' fields
                        message_string += " date=\"{}\"".format(message_timestamp)
                        if not is_sent:
                            message_string += " dateSent=\"{}\"".format(message_timestamp)
                        # always assume 'locked' = false
                        message_string += " locked=\"false\""

                        # TODO: seen
                        # TODO: read
                        message_string += " seen=\"false\" read=\"true\">"

                        # addresses
                        message_string += "<addresses>"
                        if is_sent:
                            message_string += "<address type=\"from\">insert-address-token</address>"
                        else:
                            sender = conversation.participants[message.sender_gaia_id]
                            message_string += "<address type=\"from\">{}</address>".format(
                                self._get_participant_phone_number(sender))
                        # Store the other participants
                        for participant in conversation.participants.values():
                            if participant.gaia_id != self_gaia_id and participant.gaia_id != message.sender_gaia_id:
                                message_string += "<address type=\"{}\">{}</address>".format(
                                    "from" if participant.gaia_id == message.sender_gaia_id else "to",
                                    self._get_participant_phone_number(participant))
                        message_string += "</addresses>"

                        # parts
                        order = 0
                        if message.content is not None:
                            content_is_plain = self._is_ascii(message.content)
                            message_string += MMS_PART.format("text/plain",
                                                              order,
                                                              "plain" if content_is_plain
                                                              else "base64",
                                                              escape(message.content) if content_is_plain
                                                              else self._base64_text(message.content))
                            order += 1
                        if message.attachments is not None and len(message.attachments) > 0:
                            for attachment in message.attachments:
                                if attachment.media_type is not None:
                                    if attachment.media_type == "PHOTO":
                                        data = None
                                        if attachment.original_content_url is not None:
                                            data = self._convert_url_to_base64_data(attachment.original_content_url)
                                        if data is not None:
                                            message_string += MMS_PART.format("image/jpeg", order, "base64", data)
                                            order += 1
                                        else:
                                            print("Error: unable to download image data!")
                                    elif attachment.media_type == "ANIMATED_PHOTO":
                                        data = None
                                        if attachment.original_content_url is not None:
                                            data = self._convert_url_to_base64_data(attachment.original_content_url)
                                        if data is not None:
                                            message_string += MMS_PART.format("image/gif", order, "base64", data)
                                            order += 1
                                        else:
                                            print("Error: unable to download image data!")
                                    elif attachment.media_type == "VIDEO":
                                        data = None
                                        if attachment.original_content_url is not None:
                                            data = self._convert_url_to_base64_data(attachment.original_content_url)
                                        if data is not None:
                                            message_string += MMS_PART.format("video/*", order, "base64", data)
                                            order += 1
                                        else:
                                            print("Error: unable to download video data!")
                                    else:
                                        print("Error: Attachment media type is unknown!")
                                else:
                                    print("Error: Attachment media type is unspecified!")
                        message_string += "</mms>"
                        sms_output.write(message_string)

                sms_output.write("</thread>")
            sms_output.write("</threads>")
            sms_output.close()

    @staticmethod
    def _is_ascii(text):
        # Returns true if the text only contains ASCII characters
        return len(text) == len(text.encode())

    @staticmethod
    def _base64_text(text):
        # Converts the unicode text to base64
        return base64.b64encode(bytes(text, "utf-8")).decode('utf-8')

    @staticmethod
    def _convert_url_to_base64_data(url):
        # Downloads a file and converts it to base64
        encoded_data = None
        if url is not None:
            file_name = 'tmp/' + str(uuid.uuid4())
            os.makedirs(os.path.dirname(file_name), exist_ok=True)
            for trynum in range(0,5):
                try:
                    with urllib.request.urlopen(url) as file:
                        data = file.read()
                        with open(file_name, "wb") as new_file:
                            new_file.write(data)
                            new_file.close()
                            encoded_data = base64.b64encode(open(file_name, "rb").read()).decode('utf-8')
                            os.remove(file_name)
                    break
                except urllib.request.URLError as err:
                    print("Failed to complete request for: {} on try {} because of: {} Trying again".format(url, trynum, err))

        if encoded_data is None or len(encoded_data) <= 0:
            print("Error downloading or base64 encoding attachment!")
        return encoded_data

    def _create_participant_string(self, participants, self_gaia_id):
        # Builds a string containing the participants in a conversation, excluding the user
        result = ""
        for participant in participants.values():
            # Do not include self in the list of participants
            if participant.gaia_id == self_gaia_id:
                continue
            number = self._get_participant_phone_number(participant)
            if number is not None:
                result += number + ";"
        if len(result) <= 0:
            return None
        return result.rstrip(';')

    @staticmethod
    def _get_participant_phone_number(participant):
        # Returns the phone number for a Participant
        number = None
        if participant.national_number is not None:
            number = participant.national_number
        elif participant.e164_number is not None:
            number = participant.e164_number
        elif participant.international_number is not None:
            number = participant.international_number
        return number

    @staticmethod
    def _timestamp_to_utc_string(timestamp):
        # Converts microsecond timestamp to UTC string
        (dt, microseconds) = datetime.utcfromtimestamp(timestamp / 1000000).strftime('%Y-%m-%dT%H:%M:%S.%f').split('.')
        return "%s.%03dZ" % (dt, int(microseconds) / 1000)
