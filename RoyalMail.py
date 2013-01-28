import os
import settings
import smtplib
from email.MIMEMultipart import MIMEMultipart 
from email.MIMEBase import MIMEBase 
from email.MIMEText import MIMEText 
from email.Utils import COMMASPACE, formatdate 
from email import Encoders

from_addr = settings.smtp_login

def sendMail(to, subject, text, server="mail.google.com"):
    s = smtplib.SMTP() 
    s.connect('smtp.gmail.com') 
    s.ehlo()
    s.starttls()
    s.login(from_addr, settings.smtp_password)
    msg = MIMEMultipart()
    msg['From'] = settings.smtp_login
    msg['To'] = COMMASPACE.join(to)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject
    msg.attach( MIMEText(text) )
    s.sendmail(from_addr, to, msg.as_string() )
    s.close()

if __name__ == "__main__":
    sendMail([settings.to],'Subject', 'Body')