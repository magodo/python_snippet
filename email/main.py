#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#########################################################################
# Author: Zhaoting Weng
# Created Time: Wed 16 May 2018 10:28:57 AM CST
# Description:
#########################################################################

import smtplib
from email.mime.text import MIMEText
import argparse

SMTP_SERVER = 'smtp.163.com'
SMTP_USER = 'wztdyl@163.com'
SUBJECT = 'A greet from magodo' # this is used to avoid 163 "554 DT:SPM" issue

def __send_mail(msg, passwd):
    with smtplib.SMTP(SMTP_SERVER) as smtp_server:
        smtp_server.login(SMTP_USER, passwd)
        smtp_server.send_message(msg)

def __fillin_header(msg, recivers):
    msg['Subject'] = 'A greet from magodo'
    msg['From'] = SMTP_USER
    msg['To'] = ','.join(recivers)

def send_text_msg(recivers, passwd):
    msg = MIMEText("Hello")
    __fillin_header(msg, recivers)
    __send_mail(msg, passwd)

def send_html_msg(recivers, passwd):
    def generate_content():
        out = '''
<html>
  <head></head>
  <body>
    <p>Hi!<br>
       How are you?<br>
    </p>
  </body>
</html>
'''
        return out

    content = generate_content()
    msg = MIMEText(content, 'html')
    __fillin_header(msg, recivers)
    __send_mail(msg, passwd)


__MAIL_TYPE_HANDLER__ = {'text': send_text_msg, 'html': send_html_msg}

def main(recivers, passwd, mail_type):
    __MAIL_TYPE_HANDLER__[mail_type](recivers, passwd)


if __name__  == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('passwd', help='the authentication phrase for 163 smtp service')
    parser.add_argument('recivers', nargs='+', help='reciver list')
    parser.add_argument('mail_type', choices=['text', 'html'])
    args = parser.parse_args()
    main(args.recivers, args.passwd, args.mail_type)


