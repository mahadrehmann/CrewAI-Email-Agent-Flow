import os
import base64
import requests
import re
from docx import Document
from PyPDF2 import PdfReader
from dotenv import load_dotenv
from urllib.parse import urlencode
import json

load_dotenv()

AUTHORITY = os.getenv("AUTHORITY")  # e.g., https://login.microsoftonline.com/common
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")
SCOPES = os.getenv("SCOPES", "").split()

from msal import ConfidentialClientApplication
# from .msal_cache import build_persistence
from emailcrew.msal_cache import build_persistence

def get_silent_token(request=None):
    # 1. Web request context → get from session
    if request is not None:
        token = request.session.get("access_token")
        if token:
            return token

    # 2. Scheduler context → use MSAL cache
    cache = build_persistence()
    app = ConfidentialClientApplication(
        client_id=CLIENT_ID,
        client_credential=CLIENT_SECRET,
        authority=AUTHORITY,
        token_cache=cache
    )
    accounts = app.get_accounts()
    if accounts:
        result = app.acquire_token_silent(SCOPES, account=accounts[0])
        if result and "access_token" in result:
            return result["access_token"]

    raise RuntimeError("No valid access token found. Please log in first.")


# Helper: Generate authorization URL
def get_authorization_url():
    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "response_mode": "query",
        "scope": " ".join(SCOPES),
        "prompt": "consent"
    }
    return f"{AUTHORITY}/oauth2/v2.0/authorize?{urlencode(params)}"

# Helper: Exchange auth code for token
def exchange_code_for_token(auth_code: str):
    token_url = f"{AUTHORITY}/oauth2/v2.0/token"
    data = {
        "client_id": CLIENT_ID,
        "scope": " ".join(SCOPES),
        "code": auth_code,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code",
        "client_secret": CLIENT_SECRET
    }
    response = requests.post(token_url, data=data)
    response.raise_for_status()
    return response.json()

# Convert uploaded file to text
def convert_to_txt(input_path: str, output_dir: str = "knowledge") -> str:
    os.makedirs(output_dir, exist_ok=True)
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    output_path = os.path.join(output_dir, f"{base_name}.txt")

    ext = input_path.lower().split(".")[-1]

    if ext == "docx":
        doc = Document(input_path)
        text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
    elif ext == "pdf":
        reader = PdfReader(input_path)
        text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
    elif ext == "txt":
        return input_path
    else:
        raise ValueError(f"Unsupported file type: {ext}")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)

    return output_path

# Attach file to email
def attach_attachment(file_path):
    if not os.path.exists(file_path):
        print("File not found")
        return None

    with open(file_path, "rb") as f:
        content = base64.b64encode(f.read()).decode("utf-8")

    return {
        "@odata.type": "#microsoft.graph.fileAttachment",
        "name": os.path.basename(file_path),
        "contentBytes": content
    }

# Send email with Microsoft Graph
def send_mail(access_token, message, file_name=""):
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    if file_name:
        attachment = attach_attachment(file_name)
        if attachment:
            message["message"]["attachments"] = [attachment]

    print("➡️ Sending email with payload:\n", json.dumps(message, indent=2))

    send_response = requests.post(
        "https://graph.microsoft.com/v1.0/me/sendMail",
        headers=headers,
        json=message
    )

    if send_response.status_code == 202:
        print("✅ Email sent successfully.")
    else:
        print(f"❌ Failed to send email: {send_response.status_code}")
        print(send_response.text)

# Build OneDrive download URL
def make_shares_api_url(shared_url: str) -> str:
    b64 = base64.urlsafe_b64encode(shared_url.encode("utf-8")).decode("utf-8").rstrip("=")
    return f"https://graph.microsoft.com/v1.0/shares/u!{b64}/driveItem/content"

# Download OneDrive file using Microsoft Graph
# def download_file_from_onedrive(shared_onedrive_url: str) -> str:
def download_file_from_onedrive(access_token: str, shared_onedrive_url: str) -> str:
    headers = {
        "Authorization": f"Bearer {access_token}"
        # Authorization header removed because you don't pass token here
    }

    url = make_shares_api_url(shared_onedrive_url)
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        knowledge_dir = os.path.join(os.getcwd(), "knowledge")
        os.makedirs(knowledge_dir, exist_ok=True)

        content_disp = response.headers.get("Content-Disposition", "")
        match = re.search(r'filename="(.+?)"', content_disp)

        if match:
            filename = match.group(1)
            extension = os.path.splitext(filename)[1]
        else:
            extension = ".bin"

        new_filename = f"attachment{extension}"
        file_path = os.path.join(knowledge_dir, new_filename)

        with open(file_path, "wb") as f:
            f.write(response.content)

        print(f"✅ File downloaded to: {file_path}")
        return file_path
    else:
        print(f"❌ Failed to download: {response.status_code}")
        print(response.text)
        return ""


# email_scheduler/emailcrew/src/emailcrew

# file_path = "https://1drv.ms/t/c/901cffeb62aca0b5/EatxEQM0bMRDhpcT5-umeF4BOxtRDKMdkxuJpe20PWyuJg?e=bLhKRV"

# download_file_from_onedrive( file_path)
# print("Done ✅")
