from docx import Document
from xhtml2pdf import pisa
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
                    """You are an assistant that turns poorly formatted or plain text into clean, professional HTML 
                    emails. Do not rewrite or summarize content — preserve all original words and structure, but 
                    apply standard HTML formatting suitable for email delivery. Use <p>, <strong>, <ul>, etc., as needed. 
                    The output must be valid HTML that can be inserted into a MIMEText(..., 'html') object in Python.
                    
                    You are also to add a watermark header content to the HTML. 
                    
                    add the ffg to the <style> tag </style>
                      @page {
                        margin-top: 50px;
                        margin-left: 50px;
                        margin-right:50px;
                        margin-bottom: 50px;   
                      }

                      .watermark {
                        position: fixed;
                        margin-bottom: 30px;
                        top: 5%;
                        left: 0;
                        width: 100%;
                        text-align: center;
                        opacity: 0.1;  /* Adjust opacity for watermark effect */
                        transform: rotate(-30deg);
                        z-index: -1;
                      }

                      .watermark img {
                        width: 80%;  /* Adjust image size */
                        height: auto;
                      }
                    They are the style specifications for the watermark header.
                    
                    Then after that add this to the <body> where at the very start:
                      <div class="watermark">
                        <img src="watermark.png" alt="Watermark">
                      </div>
                    """
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




def generate_pdf_from_html(html_content, filename="output.pdf"):
    with open(filename, "wb") as pdf_file:
        pisa_status = pisa.CreatePDF(html_content, dest=pdf_file)
        if pisa_status.err:
            print("Error generating PDF")
        else:
            print(f"Formatted PDF saved as {filename}")



