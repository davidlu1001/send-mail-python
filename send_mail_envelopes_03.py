#!/usr/bin/env python
# encoding: utf-8

from envelopes import Envelope

mail_from = (u'david.lu@example.com', u'From Your Name')
mail_to = [u'david.lu@example01.com', u'david.lu@example02.com']
mail_cc = [u'david.lu@example.com']

html_file = 'test_envelopes.html'
attach_file = 'myattach.txt'

smtp_server = 'smtp.office365.com'
user = 'david.lu@example.com'
passwd = 'yourpass'

envelope = Envelope(
    from_addr=mail_from,
    to_addr=mail_to,
    cc_addr=mail_cc,
    subject=u'Envelopes demo',
    html_body=open(html_file).read(),
    text_body=u"I'm a helicopter!",
)
envelope.add_attachment(attach_file)
envelope.send(smtp_server, login=user, password=passwd, tls=True)
