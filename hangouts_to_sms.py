from hangouts_parser import HangoutsParser
from titanium_backup_formatter import TitaniumBackupFormatter


# Configuration constants
HANGOUTS_JSON_FILE = 'Hangouts.json'
OUTPUT_FILE = "messages.xml"
YOUR_PHONE_NUMBER = "+11234567890"


# Parse the Hangouts data and output Titanium Backup XML
hangouts_parser = HangoutsParser()
titanium_output = TitaniumBackupFormatter()
print("Parsing Hangouts data file...")
conversations, self_gaia_id = hangouts_parser.parse_input_file(HANGOUTS_JSON_FILE, YOUR_PHONE_NUMBER)
print("Done.")
print("Converting to SMS export file...")
titanium_output.create_output_file(conversations, self_gaia_id, OUTPUT_FILE)
print("Done.")
