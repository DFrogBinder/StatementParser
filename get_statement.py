import imaplib
import email
from email.header import decode_header
import webbrowser
import os

# account credentials
username = "-"
password = "-"

# create an IMAP4 class with SSL 
mail = imaplib.IMAP4_SSL("imap.abv.bg")
# authenticate
mail.login(username, password)

# select the mailbox you want to delete in
# if you want SPAM, use "INBOX.SPAM"
mail.select("inbox")

# search for specific mail by sender
result, data = mail.uid('search', None, '(FROM "support@tradenation.com")')
# if email is not found, exit the script
if not data[0]:
    exit()

# get the list of email IDs
email_ids = data[0].split()
first_email_id = email_ids[0]
latest_email_id = email_ids[-1]

# get the raw email
result, data = mail.uid('fetch', latest_email_id, '(BODY.PEEK[])')

raw_email = data[0][1]
# parse the raw email into a message object
email_message = email.message_from_bytes(raw_email)

# walk over the message parts in this email
for part in email_message.walk():
    if part.get_content_maintype() == "multipart":
        continue
    if part.get('Content-Disposition') is None:
        continue
    filename = part.get_filename()

    if filename is not None:
        # if there is an attachment, save it
        sv_path = os.path.join('/tmp', 'attachments', filename)
        if not os.path.isfile(sv_path):
            with open(sv_path, 'wb') as f:
                f.write(part.get_payload(decode=True))
