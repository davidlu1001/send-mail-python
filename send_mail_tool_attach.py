#!/usr/bin/env python
# encoding: utf-8

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.encoders import encode_base64
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from mimetypes import guess_type
from datetime import date, datetime, timedelta
import os
import base64
import argparse


# Define email addresses to use
addr_to = ['david.lu@example.com', 'others1@example.com']
addr_cc = ['david.lu@example.com', 'others2@example.com']
addr_bcc = ['david.lu@example.com', 'others3@example.com']
addr_from = 'david.lu@example.com'

# Define SMTP email server details
smtp_server = 'smtp.office365.com'
smtp_user = 'david.lu@example.com'
port = 587
smtp_pass = 'yourpass'

# date for subject
month_last = (datetime.utcnow().replace(day=1) - timedelta(days=1)).strftime("%Y%m")


def encode(key, clear):
    enc = []
    for i in range(len(clear)):
        key_c = key[i % len(key)]
        enc_c = (ord(clear[i]) + ord(key_c)) % 256
        enc.append(enc_c)
    return base64.urlsafe_b64encode(bytes(enc))

def decode(key, enc):
    dec = []
    enc = base64.urlsafe_b64decode(enc)
    for i in range(len(enc)):
        key_c = key[i % len(key)]
        dec_c = chr((256 + enc[i] - ord(key_c)) % 256)
        dec.append(dec_c)
    return "".join(dec)


def get_mimetype(filename):
    """Returns the MIME type of the given file.

    :param filename: A valid path to a file
    :type filename: str

    :returns: The file's MIME type
    :rtype: tuple
    """

    content_type, encoding = guess_type(filename)
    if content_type is None or encoding is not None:
        content_type = "application/octet-stream"
    return content_type.split("/", 1)


def mimify_file(filename):
    """Returns an appropriate MIME object for the given file.

    :param filename: A valid path to a file
    :type filename: str

    :returns: A MIME object for the givne file
    :rtype: instance of MIMEBase
    """

    filename = os.path.abspath(os.path.expanduser(filename))
    basefilename = os.path.basename(filename)

    msg = MIMEBase(*get_mimetype(filename))
    msg.set_payload(open(filename, "rb").read())
    msg.add_header("Content-Disposition", "attachment", filename=basefilename)

    encode_base64(msg)
    return msg


def send_mail(html_file, attach_files):
    # construct email
    msg = MIMEMultipart('alternative')
    msg['To'] = ", ".join(addr_to)
    msg['Cc'] = ", ".join(addr_cc)
    msg['Bcc'] = ", ".join(addr_bcc)
    msg['From'] = addr_from
    msg['Subject'] = 'Your Report Name - ' + month_last

    # Create the body of the message (a plain-text and an HTML version).
    text = "This is a test message.\nText and html."
    html = open(html_file).read()

    # Record the MIME types of both parts - text/plain and text/html.
    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')

    # Attach parts into message container.
    msg.attach(part1)
    msg.attach(part2)

    # Attach any files
    [msg.attach(mimify_file(filename)) for filename in attach_files]

    # Send the message via an SMTP server
    s = smtplib.SMTP(smtp_server, port)
    s.ehlo()
    s.starttls()
    s.ehlo()
    s.login(smtp_user, smtp_pass)
    s.sendmail(addr_from, addr_to + addr_cc + addr_bcc, msg.as_string())
    s.quit()


def main():
    # Setup the command line argument parser.
    DESCRIPTION = ('Send Email')
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('html_file', type=str, help='a html content file, eg. email_content.html')
    parser.add_argument('attach_files', nargs='+', type=str, help='attach files, eg. vault_size_data.txt aaa.tgz')
    args = parser.parse_args()

    send_mail(args.html_file, args.attach_files)


if __name__ == '__main__':
    main()
