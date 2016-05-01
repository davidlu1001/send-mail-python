#!/usr/bin/env python
# encoding: utf-8

from envelopes import Envelope
from datetime import date, datetime, timedelta
import argparse

mail_from = (u'david.lu@example.com', u'From Name')
mail_to = [u'david.lu@example.com', u'others@example.com']
mail_cc = [u'david.lu@example.com']

smtp_server = 'smtp.office365.com'
user = 'david.lu@example.com'
passwd = 'yourpass'

month_last = (datetime.utcnow().replace(day=1) - timedelta(days=1)).strftime("%Y%m")


def send_mail(html_file, attach_file):
    envelope = Envelope(
        from_addr=mail_from,
        to_addr=mail_to,
        cc_addr=mail_cc,
        subject='Test Report - ' + month_last,
        html_body=open(html_file).read(),
    )
#    envelope.add_attachment(attach_file)
    print("begin to send: {}".format(html_file))
    envelope.send(smtp_server, login=user, password=passwd, tls=True)


def main():
    # Setup the command line argument parser.
    DESCRIPTION = ('Send Email')
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('html_file', type=str, help='a html content file, eg. email_content.html')
    parser.add_argument('attach_file', type=str, help='an attach file, eg. vault_size_data.txt')
    args = parser.parse_args()

    send_mail(args.html_file, args.attach_file)


if __name__ == '__main__':
    main()
