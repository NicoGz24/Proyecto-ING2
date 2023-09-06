import smtplib, ssl
from email.message import EmailMessage

## "ingsoft2juanperez1970"

def send_email(subject: str, to: str, message: str, password: str ="ixkkpqxqmkwrlcoi", sender: str = "perez24juan1970@gmail.com"):
    msg = EmailMessage()
    msg.set_content(message)

    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = to
    password = password


    # Send the message via our own SMTP server.
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.login(sender, password)
    server.send_message(msg)
    server.quit()