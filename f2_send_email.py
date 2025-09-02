import os
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from f1_generate_pdf import clean_markdown_html_block, format_as_html_email_with_ai




# using temp file
import os
from xhtml2pdf import pisa
def generate_pdf_from_html(html_content, filename="output.pdf"):
    # Store inside /tmp so Render allows it
    tmp_path = os.path.join("/tmp", filename)

    with open(tmp_path, "wb") as pdf_file:
        pisa_status = pisa.CreatePDF(html_content, dest=pdf_file)

    if pisa_status.err:
        print("Error generating PDF")
        return None  # indicate failure
    else:
        print(f"Formatted PDF saved at {tmp_path}")
        return tmp_path  # return path so caller can send it


"""
import os
from xhtml2pdf import pisa

def generate_pdf_from_html(html_content, filename="output.pdf"):
    with open(filename, "wb") as pdf_file:
        pisa_status = pisa.CreatePDF(html_content, dest=pdf_file)

    if pisa_status.err:
        print("Error generating PDF")
        return None
    else:
        abs_path = os.path.abspath(filename)  # full path for clarity
        print(f"Formatted PDF saved at {abs_path}")
        return abs_path
"""






# ............................................................
# 🔹 FUNCTION: Encode and Send Email For Reminder Service
# ............................................................
import json
import base64
from openai import OpenAI
from google.oauth2 import service_account
from googleapiclient.discovery import build
from email.mime.text import MIMEText


# ............................................................
# 🔹 CONFIGURATION
# ............................................................
# ✅ OpenAI Client
client = OpenAI()

# ✅ Gmail API Configuration
#SERVICE_ACCOUNT_FILE = 'oma_baby_full_google.json'  # Ensure correct path
#USER_EMAIL = 'bolu@casialab.com'  # Sender's email

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # directory of current file
SERVICE_ACCOUNT_FILE = os.path.join(BASE_DIR, "welbridg-agent.json")
#SERVICE_ACCOUNT_FILE = 'welbridg-agent.json'  # Ensure correct path
USER_EMAIL = 'percival@log10media.com'  # Sender's email
SCOPES = ['https://mail.google.com/']

# Authenticate Gmail API
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES, subject=USER_EMAIL
)
api_resource = build('gmail', 'v1', credentials=credentials)




def send_email_to_staff(to, subject, body, pdf_path=None):
    """
    Sends an email using the Gmail API. Optionally attaches a PDF file.
    """
    try:
        if not to or not subject or not body:
            raise ValueError("Missing required email fields: 'to', 'subject', or 'body'.")

        # Create a multipart email message
        message = MIMEMultipart()
        message["to"] = to
        message["from"] = USER_EMAIL
        message["subject"] = subject

        # Attach HTML body
        html_body = clean_markdown_html_block(format_as_html_email_with_ai(body))
        message.attach(MIMEText(html_body, "html"))

        # Optional PDF attachment
        if pdf_path and os.path.exists(pdf_path):
            with open(pdf_path, "rb") as f:
                part = MIMEApplication(f.read(), _subtype="pdf")
                part.add_header("Content-Disposition", "attachment", filename=os.path.basename(pdf_path))
                message.attach(part)

        # Encode full message in Base64
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        # Send email
        sent_message = api_resource.users().messages().send(
            userId="me", body={"raw": raw_message}
        ).execute()

        print(f"✅ Email with PDF sent successfully to {to}!")
        return {"status": "success", "sent_to": to, "subject": subject}

    except Exception as e:
        print(f"❌ Error sending email: {e}")
        return {"status": "error", "error": str(e)}
