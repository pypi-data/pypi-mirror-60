#!/bin/env python

#######################################################################
#
# Copyright (C) 2020 David Palao
#
# This file is part of SPerATo.
#
#  SPerATo is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  SPerATo is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with SPerATo.  If not, see <http://www.gnu.org/licenses/>.
#
#######################################################################

import sys
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class SPerAToListEmail:
    def __init__(self, to, subject):
        self.to = to.split(",")
        self.subject = subject
        self.body = []
        self.msg = MIMEMultipart()
        self.attachment = None
        
    def feed(self, line):
        self.body.append(line)
        
    def send(self, body=None):
        try:
            if body is None:
                body = "\n".join(self.body)
            txt_msg = MIMEText(body)
            self.msg['Subject'] = self.subject
            self.msg['From'] = "SPerATo"
            self.msg['To'] = ",".join(self.to)
            self.msg.attach(txt_msg)
            if self.attachment:
                self.msg.attach(self.attachment)
            server = smtplib.SMTP('localhost')
            server.send_message(self.msg)
            server.quit()
        except:
            print("Could not send email", file=sys.stderr)
        else:
            print("email correctly sent to {0}".format(",".join(self.to)), 
                file=sys.stderr)

    def attach(self, contents_file_name, attached_name=None):
        with open(contents_file_name, "r") as f:
            self.attachment = MIMEText(f.read())
        self.attachment.add_header("Content-Disposition", "attachment", 
            filename=attached_name)
