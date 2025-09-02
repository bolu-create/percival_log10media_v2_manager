from dotenv import load_dotenv
#from langchain.llms import OpenAI
import os
from dotenv import load_dotenv


# Load environment variables
load_dotenv()

# ............................................................
# 🔹 FUNCTION: Encode and Send Email For Reminder Service
# ............................................................
import json
import base64
from openai import OpenAI
from google.oauth2 import service_account
from googleapiclient.discovery import build
from email.mime.text import MIMEText





from openai import OpenAI

def format_as_html_email_with_ai(raw_text):
    """
    Uses OpenAI to convert raw plain text into well-structured HTML email content.
    The email's content will not be changed, only formatted with headings, bold text, and paragraph structure.
    """
    client = OpenAI()
    
    completion = client.chat.completions.create(
        model="gpt-4o",  # You can switch to "gpt-4" if needed
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an assistant that turns poorly formatted or plain text into clean, professional HTML "
                    "emails. Do not rewrite or summarize content — preserve all original words and structure, but "
                    "apply standard HTML formatting suitable for email delivery. Use <p>, <strong>, <ul>, etc., as needed. "
                    "The output must be valid HTML that can be inserted into a MIMEText(..., 'html') object in Python."
                )
            },
            {
                "role": "user",
                "content": raw_text
            }
        ]
    )
    
    html_output = completion.choices[0].message.content.strip()
    return html_output




def clean_markdown_html_block(text):
    """Removes triple backtick markdown wrapper from HTML content."""
    if text.startswith("```html"):
        text = text[7:]  # remove ```html\n
    if text.endswith("```"):
        text = text[:-3]  # remove trailing ```
    return text.strip()





from openai import OpenAI
def emailer(statement):
    client = OpenAI()
    completion = client.chat.completions.create(
        model="gpt-4.1",
        #model="o1",
        #reasoning_effort="high",
        store=True,
        messages=[
            {"role": "system", "content": f"""
                Your name is Percival, a helpful assistant whose job is to help draft emails about staffs who did not respond to the KPI progress update emails sent across. This will be sent to their manager. 
                You are to carry the tone of a performance coach in the company, as this is what you are, as you are basically informing the manager of the people who didn't respond to the emails and for them to take necessary steps or even steps you can recommend for the manager to motivate them to respond to the emails. 
                So you are not necessarily reporting them for any wrong-doing, just informing their manager of their lack of response and giving tips for him/her to inform and encouragethem to respond.
                
                Now the names of the staffs will be given to you. Compose the remainder of the message as instructed. 
         
            """},
            {"role": "user", "content": statement}
        ]
    )
    # Ensure the response is in valid JSON format
    response_text = completion.choices[0].message.content.strip()
    return response_text




# ............................................................
# 🔹 CONFIGURATION
# ............................................................
# ✅ OpenAI Client
client = OpenAI()

# ✅ Gmail API Configuration
#SERVICE_ACCOUNT_FILE = 'oma_baby_full_google.json'  # Ensure correct path
#USER_EMAIL = 'bolu@casialab.com'  # Sender's email
SERVICE_ACCOUNT_FILE = 'welbridg-agent.json'  # Ensure correct path
USER_EMAIL = 'percival@log10media.com'  # Sender's email
SCOPES = ['https://mail.google.com/']

# Authenticate Gmail API
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES, subject=USER_EMAIL
)
api_resource = build('gmail', 'v1', credentials=credentials)



def send_email_to_staff_for_no_response(to, subject, body):
    """Sends an email using the Gmail API with proper Base64 encoding. for user's reminders"""
    try:
        if not to or not subject or not body:
            raise ValueError("Missing required email fields: 'to', 'subject', or 'body'.")
  
        html_body = clean_markdown_html_block(format_as_html_email_with_ai(emailer(body)))

        # Create the email message
        message = MIMEText(html_body, "html")
        
        message["to"] = to
        message["from"] = USER_EMAIL
        message["subject"] = subject

        # Encode in Base64
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        # Send email
        sent_message = api_resource.users().messages().send(
            userId="me", body={"raw": raw_message}
        ).execute()

        print(f"✅ Email sent successfully to {to}!")
        return {"status": "success", "sent_to": to, "subject": subject}

    except Exception as e:
        print(f"❌ Error sending email: {e}")
        return {"status": "error", "error": str(e)}
