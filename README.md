Hangouts to SMS/MMS
======

### Note: This is not currently maintained and reportedly no longer works as-is.

Scripts to convert exported Hangouts SMS/MMS messages to an SMS XML file.
 This is intended for Project Fi users that have been using Hangouts for texting along with the
 "Project Fi calls and SMS" option enabled who want to switch back to normal SMS/MMS apps.

 These scripts and steps will allow you to export your Project Fi SMS/MMS messages from the Hangouts "cloud" and import them into the normal SMS/MMS database on your phone, thus retaining your message history.

## Liability, etc
**Use at your own risk!** I claim no responsibility for the results of using these scripts or the steps outlined below. I do not provide any warranty or support.

## Requirements:
* Python 3
* Titanium Backup **PRO**
* Rooted Android Device

## Notes:
* Titanium backup will overwrite the existing SMS/MMS database on the phone.
* Root **is** required, Google removed non root functionality for Titanium Backup SMS backup/restore.

## Phone Setup:
1. Install Titanium Backup **PRO** (root **is** required for SMS/MMS backup/restore)
2. Backup existing SMS/MMS messages using Titanium backup:
    * Open Titanium Backup
    * Press 'MENU' at the top right
    * Scroll down and select 'Backup data to XML...'
    * Select 'Messages (SMS & MMS)'
    * When it's finished, select 'Save file locally', and hit 'SAVE' (remember where you saved it)
3. Clear existing data from your SMS app:
    * Go into Settings and select 'Apps'
    * Select your preferred SMS app (e.g., Messenger or Textra)
    * Select 'Storage'
    * Select 'CLEAR DATA'

## Export Hangouts Messages:
1. Open https://takeout.google.com/settings/takeout
2. Under 'Select data to include', click the 'Select none' button
3. Scroll down and enable only Hangouts
4. Scroll down and click 'Next'
5. Increase 'Archive size (max)' to 4GB (hopefully not necessary)
6. Choose 'Delivery method' and click 'Create archive'
7. Download it to your computer when it's finished

## Converting Hangouts to Titanium Backup XML:
1. Edit "YOUR_PHONE_NUMBER" variable in hangouts_to_sms.py to contain your cell number.
    * This is because the number seems to be missing from some conversations.
2. Extract the Hangouts archive and copy the Hangouts.json file to the same folder as the script.
2. Run the hangouts_to_sms.py script

## Importing XML using Titanium Backup:
1. Copy the messages.xml output file to your phone (I used Google Drive to transfer it)
2. Open Titanium Backup
3. Press 'MENU' at the top right
4. Scroll down and select 'Restore data from XML...'
5. Select 'Messages (SMS & MMS)'
6. Select the messages.xml file from wherever you saved it on your phone
7. If prompted to set Titanium Backup as your default SMS app, allow it
    * It will change it back after it is finished
8. When it's finished, open your texting app of choice and wait a bit for it to parse through the new messages
