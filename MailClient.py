from smtplib import SMTP_SSL as SMTP
from email.mime.text import MIMEText
import threading

class MailClient:

    def __init__(self, data):
        self.data = data
        self.login = raw_input("mail login:")
        self.password = raw_input("password:")
        self.provider = "mail.de"

    def __send_message(self, subject, content, recipients):
        text = content
        message = MIMEText(text, 'plain')
        message['Subject'] = subject
        my_email = self.login + '@' + self.provider
        message['To'] = ', '.join(recipients)

        try:
            connection = SMTP("smtp." + self.provider, timeout=30)
            connection.set_debuglevel(True)
            connection.login(self.login, self.password)
            try:
                connection.sendmail(my_email, recipients, message.as_string())
            finally:
                connection.close()
        except Exception as exc:
            print("sending mail failed")

    def notify_users(self):
        subject = "Bewegung erkannt"
        message = "Haben Sie sich gerade bewegt? Falls nein, werden Sie wahrscheinlich gerade ausgeraubt."
        recipients = [mail.address for mail in self.data.get_mails().values() if mail.notify]
        thread = threading.Thread(target=self.__send_message, args=[subject, message, recipients])
        thread.start()