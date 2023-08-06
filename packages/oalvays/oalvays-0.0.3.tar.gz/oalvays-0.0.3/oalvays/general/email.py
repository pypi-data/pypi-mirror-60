import smtplib
from email.mime.text import MIMEText

class email_session:
    def __init__(self, address, authword, host = 'default'):
        if [type(address), type(authword), type(host)] != [str, str, str]:
            raise TypeError('all arguments taken should be string')
        self.address = address
        self.authword = authword
        self.host = "smtp." + address.split("@")[1] if host == 'default' else host
        self.receivers = []
        
    def __repr__(self):
        return "'address': {0}\n'authword': {1}\n'host': {2}\n'receivers': {3}".format(self.address,
                        self.authword, self.host, self.receivers)
    
    def sendlist(self, receivers):
        """receivers should be a list"""
        if type(receivers) != list:
            raise TypeError('receivers should be a list')
        self.receivers = receivers
        
    def send_email(self, title, content):
        message = MIMEText(content,'plain','utf-8')
        message['Subject'] = title 
        message['From'] = self.address 
        message['To'] = self.receivers[0]
        
        smtpObj = smtplib.SMTP_SSL(self.host)                # connect to server
        smtpObj.login(self.address, self.authword)           # login
        smtpObj.sendmail(
            self.address,self.receivers,message.as_string()) # send email
        smtpObj.quit()                                       # quit
        #except smtplib.SMTPException as e: