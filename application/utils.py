from application import mail
from flask_mail import Message

def send_contact_email(name, email, subject, message):
    msg = Message('The Locker - Contact Us Email', sender='The Locker', recipients=[
                  "ronnachum13@gmail.com", "shreygupta04@gmail.com", "nljbritto@gmail.com"])
    msg.body = f'''A New User Submitted a Contact Form:
        Name: {name}
        Email: {email}
        Subject: {subject}
        Message:
        {message}
    '''
    mail.send(msg)