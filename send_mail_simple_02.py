#!/usr/bin/env python
# encoding: utf-8

# Import smtplib to provide email functions
import smtplib

# Import the email modules
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Define email addresses to use
addr_to = 'david.lu@example.com'
addr_from = 'david.lu@example.com'

# Define SMTP email server details
smtp_server = 'smtp.office365.com'
smtp_user = 'david.lu@example.com'
port = 587
smtp_pass = 'yourpass'

# Construct email
msg = MIMEMultipart('alternative')
msg['To'] = addr_to
msg['From'] = addr_from
msg['Subject'] = 'Test Email From RPi'

# Create the body of the message (a plain-text and an HTML version).
text = "This is a test message.\nText and html."
html = """\
<html>
  <head></head>
  <body>
    <p>This is a test message.</p>
    <p>Text and HTML</p>
  </body>
</html>
"""

# Record the MIME types of both parts - text/plain and text/html.
part1 = MIMEText(text, 'plain')
part2 = MIMEText(html, 'html')

# Attach parts into message container.
# According to RFC 2046, the last part of a multipart message, in this case
# the HTML message, is best and preferred.
msg.attach(part1)
msg.attach(part2)

# Send the message via an SMTP server
# Determine how we want to begin the connection
s = smtplib.SMTP(smtp_server, port)
s.ehlo()
s.starttls()
s.ehlo()
s.login(smtp_user, smtp_pass)
s.sendmail(addr_from, addr_to, msg.as_string())
s.quit()
