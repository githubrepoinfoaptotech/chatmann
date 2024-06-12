import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from pprint import pprint
import os
from dotenv import load_dotenv 
import base64
load_dotenv()
# Create a SendinBlue API configuration
configuration = sib_api_v3_sdk.Configuration()

# Replace "<your brevo api key here>" with your actual SendinBlue API key
configuration.api_key['api-key'] = os.environ.get('myemailtoken')
# name=str(os.environ.get('senderMail'))
# email=str(os.environ.get('senderName'))
name="Infoapto Technologies"
email="info@infoaptotech.com"
# Initialize the SendinBlue API instance
api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

def send_verification_email(subject, html, to_address=None, receiver_username=None):
    # SendinBlue mailing parameters
    subject = subject
    sender = {"name": name, "email": email}
    html_content = html

    # Define the recipient(s)
    if to_address:
        # You can add multiple email accounts to which you want to send the mail in this list of dicts
        to = [{"email": to_address, "name": receiver_username}]

    # Create a SendSmtpEmail object
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(to=to, html_content=html_content, sender=sender, subject=subject)

    try:
        # Send the email
        api_response = api_instance.send_transac_email(send_smtp_email)
        print(api_response)
        return True
    except ApiException as e:
         print("Exception when calling SMTPApi->send_transac_email: %s\n" % e)

def send_invoice(subject, html, to_address=None, receiver_username=None, attachment=None):
     # SendinBlue mailing parameters
    subject = subject
    sender = {"name": name, "email": email}
    html_content = html

    # Define the recipient(s)
    if to_address:
        # You can add multiple email accounts to which you want to send the mail in this list of dicts
        to = [{"email": to_address, "name": receiver_username}]
    print(attachment)
    # Create a SendSmtpEmail object
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(to=to, html_content=html_content, sender=sender, subject=subject)
    # Attach the file
    if attachment:
        # Get the file name
        file_name = os.path.basename(attachment)
        with open(attachment, 'rb') as file:
            # Read file content
            file_data = file.read()
            # Encode file content to base64
            file_data_base64 = base64.b64encode(file_data).decode('utf-8')
            # Set attachment
            send_smtp_email.attachment = [{"name": file_name, "content": file_data_base64}]

    try:
        # Send the email
        api_response = api_instance.send_transac_email(send_smtp_email)
        print(api_response)
        return True
    except ApiException as e:
         print("Exception when calling SMTPApi->send_transac_email: %s\n" % e)
         
def send_verification_quota(subject, html, to_address=None, receiver_username=None):
    # SendinBlue mailing parameters
    subject = subject
    sender = {"name": name, "email": email}
    html_content = html

    # Define the recipient(s)
    if to_address:
        # You can add multiple email accounts to which you want to send the mail in this list of dicts
        to = [{"email": to_address, "name": receiver_username}]

    # Create a SendSmtpEmail object
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(to=to, html_content=html_content, sender=sender, subject=subject)

    try:
        # Send the email
        api_response = api_instance.send_transac_email(send_smtp_email)
        print(api_response)
        return True
    except ApiException as e:
         print("Exception when calling SMTPApi->send_transac_email: %s\n" % e)
def send_reset_password_mail(subject, html, to_address=None, receiver_username=None):
    # SendinBlue mailing parameters
    subject = subject
    sender = {"name": name, "email": email}
    html_content = html

    # Define the recipient(s)
    if to_address:
        # You can add multiple email accounts to which you want to send the mail in this list of dicts
        to = [{"email": to_address, "name": receiver_username}]

    # Create a SendSmtpEmail object
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(to=to, html_content=html_content, sender=sender, subject=subject)

    try:
        # Send the email
        api_response = api_instance.send_transac_email(send_smtp_email)
        print(api_response)
        return True
    except ApiException as e:
         print("Exception when calling SMTPApi->send_transac_email: %s\n" % e)
def send_customer_inquiry(subject, html, to_address=None, receiver_username=None):
    # SendinBlue mailing parameters
    subject = subject
    print(name)
    print(email)
    sender = {"name": name, "email": email}
    html_content = html

    # Define the recipient(s)
    if to_address:
        # You can add multiple email accounts to which you want to send the mail in this list of dicts
        to = [{"email": to_address, "name": receiver_username}]

    # Create a SendSmtpEmail object
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(to=to, html_content=html_content, sender=sender, subject=subject)

    try:
        # Send the email
        api_response = api_instance.send_transac_email(send_smtp_email)
        print(api_response)
        return True
    except ApiException as e:
         print("Exception when calling SMTPApi->send_transac_email: %s\n" % e)