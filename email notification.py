# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
import imghdr
import smtplib

from datetime import datetime
from email.message import EmailMessage

import config_bestbuy


distribution = ['email1@email.com', 'eamil2@email.com']
email_user = config_bestbuy.email_user
sender = config_bestbuy.email_sender
user = config_bestbuy.user
password = config_bestbuy.email_password

subject = 'My Notification'
body = f'Notification sent (UTC): {datetime.now()}\nby {sender}'

msg = EmailMessage()
msg['Subject'] = subject
msg['From'] = sender
msg['To'] = distribution
msg.set_content(body)

# %%
def send_email_localhost():
    """
    start localhost debugger
    python -m smtpd -c DebuggingServer -n localhost:1025
    """
    with smtplib.SMTP('localhost', 1025) as smtp_server:
        msg = f"Subject: {subject}\n\n{body}"

        smtp_server.sendmail(
            from_addr=sender, 
            to_addrs=distribution,
            msg=msg
        )


def send_email_basic():

    with smtplib.SMTP('smtp.privateemail.com', 587) as smtp_server:
        msg = f"Subject: {subject}\n\n{body}"

        smtp_server.ehlo() # identify server login
        smtp_server.starttls()
        smtp_server.ehlo() # re-identify with encryption
        smtp_server.login(email_user, password)
        smtp_server.sendmail(
            from_addr=sender, 
            to_addrs=distribution,
            msg=msg
        )


def send_email_basic_encrypted():

    with smtplib.SMTP_SSL('smtp.privateemail.com', 465) as smtp_server:
        msg = f"Subject: {subject}\n\n{body}"

        smtp_server.login(email_user, password)
        smtp_server.sendmail(
            from_addr=sender, 
            to_addrs=distribution,
            msg=msg
        )


def send_email_advanced_encrypted():

    with smtplib.SMTP_SSL('smtp.privateemail.com', 465) as smtp_server:
        smtp_server.login(email_user, password)
        smtp_server.send_message(msg)


def send_email_advanced_encrypted_with_image_attachment():
    images = ['image1.jpg', 'image2.tnf']
    for image in images:
        with open(image, 'rb') as f:
            file_data = f.read()
            file_type = imghdr.what(f.fileno)
            file_name = f.name
        msg.add_attachment(file_data, maintype='image', subtype=file_type, filename=file_name)

    with smtplib.SMTP_SSL('smtp.privateemail.com', 465) as smtp_server:
        smtp_server.login(email_user, password)
        smtp_server.send_message(msg)


def send_email_advanced_encrypted_with_pdf_attachment():
    files = ['file1.pdf', 'file2.pdf']
    for file in files:
        with open(file, 'rb') as f:
            file_data = f.read()
            file_name = f.name
        msg.add_attachment(file_data, maintype='application', subtype='octet-stream', filename=file_name)

    with smtplib.SMTP_SSL('smtp.privateemail.com', 465) as smtp_server:
        smtp_server.login(email_user, password)
        smtp_server.send_message(msg)


def send_email_advanced_encrypted_html():
    
    msg.add_alternative("""\
<!DOCTYPE html>
<html lang="en">
<body>
    <h1 style="color:steelblue">This is an HTML email!</h1>
</body>
</html>
    
""", subtype='html')

    with smtplib.SMTP_SSL('smtp.privateemail.com', 465) as smtp_server:
        smtp_server.login(email_user, password)
        smtp_server.send_message(msg)


# %%

if __name__ == "__main__":
    send_email_advanced_encrypted()