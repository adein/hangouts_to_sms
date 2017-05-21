#!/usr/bin/python3

import sys
import argparse

from hangouts_parser import HangoutsParser
from titanium_backup_formatter import TitaniumBackupFormatter

def main():
    parser = argparse.ArgumentParser(description="Run logs on subrepos recursively")
    parser.add_argument("-ph", "--phonenumber", type=str, help="your phone number", required=True)
    parser.add_argument("-of", "--outfile", type=str, help="file to write to", default="messages.xml")
    parser.add_argument("-if", "--infile", type=str, help="file to read from", default="Hangouts.json")
    args = parser.parse_args()

    # Parse the Hangouts data and output Titanium Backup XML
    print("Parsing Hangouts data file...")
    hangouts_parser = HangoutsParser()
    conversations, self_gaia_id = hangouts_parser.parse_input_file(args.infile, args.phonenumber)
    print("Done.")

    print("Converting to SMS export file...")
    titanium_output = TitaniumBackupFormatter()
    titanium_output.create_output_file(conversations, self_gaia_id, args.outfile)
    print("Done.")

    return 0


if __name__ == '__main__':
    sys.exit(main())

