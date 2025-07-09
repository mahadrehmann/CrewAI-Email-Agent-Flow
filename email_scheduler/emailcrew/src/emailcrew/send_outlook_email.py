# send_outlook_email.py

import os
import base64
import requests
from msal import ConfidentialClientApplication, SerializableTokenCache
from dotenv import load_dotenv
import re
from docx import Document
from PyPDF2 import PdfReader

# ------------------------------------------------------------------------------
# Helpers: Token Management
# ------------------------------------------------------------------------------

def get_token():
    """
    Acquire an access token silently from cache, or error if none found.
    Assumes you've already done the browser-based sign-in at /auth/login/.
    """
    load_dotenv()

    client_id     = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")
    authority     = os.getenv("AUTHORITY")
    scopes        = os.getenv("SCOPES", "").split()
    cache_path    = os.getenv("TOKEN_CACHE", "token_cache.bin")

    # 1) Initialize the token cache
    cache = SerializableTokenCache()
    if os.path.exists(cache_path):
        cache.deserialize(open(cache_path, "r").read())

    # 2) Create the ConfidentialClientApplication
    app = ConfidentialClientApplication(
        client_id=client_id,
        authority=authority,
        client_credential=client_secret,
        token_cache=cache
    )

    # 3) Try to get a token silently
    accounts = app.get_accounts()
    if accounts:
        result = app.acquire_token_silent(scopes, account=accounts[0])
        if result and "access_token" in result:
            return result["access_token"]

    # 4) No token in cache → the user must have visited /auth/login/
    raise RuntimeError(
        "No access token found in cache. "
        "Redirect the user to /auth/login/ to sign in."
    )

# ------------------------------------------------------------------------------
# File Conversion & Attachment Helpers
# ------------------------------------------------------------------------------

def convert_to_txt(input_path: str, output_dir: str = "knowledge") -> str:
    """Converts .docx/.pdf to .txt, returns the .txt path."""
    os.makedirs(output_dir, exist_ok=True)
    base_name   = os.path.splitext(os.path.basename(input_path))[0]
    output_path = os.path.join(output_dir, f"{base_name}.txt")
    ext = input_path.lower().split(".")[-1]

    if ext == "docx":
        doc  = Document(input_path)
        text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    elif ext == "pdf":
        reader = PdfReader(input_path)
        text   = "\n".join(
            page.extract_text() or "" for page in reader.pages
        ).strip()
    elif ext == "txt":
        return input_path
    else:
        raise ValueError(f"Unsupported file type: {ext}")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)
    return output_path

def attach_attachment(file_path: str) -> dict:
    """Read a file and return a Graph API fileAttachment JSON."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Attachment not found: {file_path}")
    with open(file_path, "rb") as f:
        content_b64 = base64.b64encode(f.read()).decode("utf-8")
    return {
        "@odata.type": "#microsoft.graph.fileAttachment",
        "name": os.path.basename(file_path),
        "contentBytes": content_b64
    }

# ------------------------------------------------------------------------------
# Graph API Calls
# ------------------------------------------------------------------------------

def send_mail(message: dict, file_name: str = ""):
    """
    Sends an email via Graph API.  message should be the JSON payload under "message".
    If file_name is provided, the attachment is added.
    """
    token = get_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    if file_name:
        message.setdefault("message", {})\
               .setdefault("attachments", [])\
               .append(attach_attachment(file_name))

    response = requests.post(
        "https://graph.microsoft.com/v1.0/me/sendMail",
        headers=headers,
        json={"message": message.get("message", message)}
    )
    if response.status_code == 202:
        print("✅ Email sent successfully!")
    else:
        raise RuntimeError(
            f"❌ Failed to send email: {response.status_code}\n{response.text}"
        )

def make_shares_api_url(shared_url: str) -> str:
    """
    Given a OneDrive share link, returns the Graph endpoint to download the file.
    """
    b64 = base64.urlsafe_b64encode(shared_url.encode("utf-8"))\
                  .decode("utf-8")\
                  .rstrip("=")
    return f"https://graph.microsoft.com/v1.0/shares/u!{b64}/driveItem/content"

def download_file_from_onedrive(shared_onedrive_url: str) -> str:
    """
    Downloads a OneDrive shared file via Graph and saves it under ./knowledge/.
    Returns the filename saved.
    """
    token   = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    url     = make_shares_api_url(shared_onedrive_url)

    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        raise RuntimeError(
            f"❌ Failed to download file: {resp.status_code}\n{resp.text}"
        )

    # Pull filename from Content-Disposition if available
    disp = resp.headers.get("Content-Disposition", "")
    m    = re.search(r'filename="(.+?)"', disp)
    ext  = os.path.splitext(m.group(1))[1] if m else ""
    fname = f"attachment{ext}"
    outdir = os.path.join(os.getcwd(), "knowledge")
    os.makedirs(outdir, exist_ok=True)
    fullpath = os.path.join(outdir, fname)

    with open(fullpath, "wb") as f:
        f.write(resp.content)

    print(f"✅ File downloaded and saved to: {fullpath}")
    return fname

# import os
# import base64
# import requests
# from msal import PublicClientApplication, SerializableTokenCache
# from dotenv import load_dotenv
# import re
# from docx import Document
# from PyPDF2 import PdfReader
# import urllib.parse

# #here ehre

# def convert_to_txt(input_path: str, output_dir: str = "knowledge") -> str:
#     """Converts .docx or .pdf file to .txt, returns path to .txt file."""
#     os.makedirs(output_dir, exist_ok=True)
#     base_name = os.path.splitext(os.path.basename(input_path))[0]
#     output_path = os.path.join(output_dir, f"{base_name}.txt")

#     ext = input_path.lower().split(".")[-1]

#     if ext == "docx":
#         doc = Document(input_path)
#         text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
#     elif ext == "pdf":
#         reader = PdfReader(input_path)
#         text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
#     elif ext == "txt":
#         return input_path  # Already text
#     else:
#         raise ValueError(f"Unsupported file type: {ext}")

#     with open(output_path, "w", encoding="utf-8") as f:
#         f.write(text)

#     return output_path

# def attach_attachment(file_path):
#     if not os.path.exists(file_path):
#         print('file not found')
#         return
    
#     with open(file_path, 'rb') as upload:
#         media_content = base64.b64encode(upload.read())

#     data_body = {
#         '@odata.type': '#microsoft.graph.fileAttachment',
#         'contentBytes': media_content.decode('utf-8'),
#         'name': os.path.basename(file_path)
#     }
#     return data_body


# def send_mail(message, file_name=""):
    
#     load_dotenv()

#     client_id = os.getenv("CLIENT_ID")
#     # tenant_id = os.getenv("TENANT_ID")
#     authority = os.getenv("AUTHORITY")
#     scopes = os.getenv("SCOPES", "").split()

#     # Initialize cache
#     cache = SerializableTokenCache()
#     if os.path.exists("token_cache.bin"):
#         cache.deserialize(open("token_cache.bin", "r").read())

#     # Initialize MSAL app with cache
#     app = PublicClientApplication(
#         client_id=client_id,
#         authority=authority,
#         token_cache=cache
#     )

#     # Try silent login
#     accounts = app.get_accounts()
#     if accounts:
#         result = app.acquire_token_silent(scopes, account=accounts[0])
#     else:
#         # Fallback to device flow login
#         # flow = app.initiate_device_flow(scopes=scopes)
#         flow = app.initiate_device_flow(scopes=scopes, extra_query_parameters={"prompt": "consent"})

#         print("Flow created:", flow)


#         if "user_code" not in flow:
#             raise Exception("Failed to create device flow")
#         print(f"\nPlease go to {flow['verification_uri']} and enter the code: {flow['user_code']}\n")
#         result = app.acquire_token_by_device_flow(flow)

#     print("RESULT after device flow:", result)

#     # Save token cache to file
#     with open("token_cache.bin", "w") as f:
#         f.write(cache.serialize())

#     # Proceed if token acquired
#     print("Scopes in token:", result.get("scope"))
#     if "access_token" in result:
#         access_token = result["access_token"]
#         print("✅ Access token acquired.")

#         # Get the logged-in user's email
#         user_info = requests.get(
#             "https://graph.microsoft.com/v1.0/me",
#             headers={"Authorization": f"Bearer {access_token}"}
#         ).json()
#         user_email = user_info.get("mail") or user_info.get("userPrincipalName")
#         print(f"📧 Logged in as: {user_email}")

#         # if file is not empty, do this:
#         if file_name != "":
#             message["message"]["attachments"] = [
#                 attach_attachment(file_name)
#             ]
        
#         print("\n\n--------SENDING THIS:\n", message)
#         # Send email
#         send_response = requests.post(
#             "https://graph.microsoft.com/v1.0/me/sendMail",
#             headers={
#                 "Authorization": f"Bearer {access_token}",
#                 "Content-Type": "application/json"
#             },
#             json=message
#         )

#         if send_response.status_code == 202:
#             print("✅ Email sent successfully!")
#         else:
#             print(f"❌ Failed to send email: {send_response.status_code}\n{send_response.text}")
#     else:
#         print("❌ Failed to acquire token:", result.get("error_description"))


# def make_shares_api_url(shared_url: str) -> str:
#     # Graph wants the URL base64‐URL‐encoded without padding:
#     b64 = base64.urlsafe_b64encode(shared_url.encode("utf-8")).decode("utf-8").rstrip("=")
#     return f"https://graph.microsoft.com/v1.0/shares/u!{b64}/driveItem/content"

# def download_file_from_onedrive(shared_onedrive_url):
#     load_dotenv()
#     new_filename = ""
#     client_id = os.getenv("CLIENT_ID")
#     authority = os.getenv("AUTHORITY")
#     scopes = os.getenv("SCOPES", "").split()

#     cache = SerializableTokenCache()
#     if os.path.exists("token_cache.bin"):
#         cache.deserialize(open("token_cache.bin", "r").read())

#     app = PublicClientApplication(client_id=client_id, authority=authority, token_cache=cache)

#     accounts = app.get_accounts()
#     result = None
#     if accounts:
#         result = app.acquire_token_silent(scopes, account=accounts[0])

#     if not result:
#         flow = app.initiate_device_flow(scopes=scopes)
#         if "user_code" not in flow:
#             raise Exception("Failed to create device flow")
#         print(f"\n🔐 Please go to {flow['verification_uri']} and enter the code: {flow['user_code']}")
#         result = app.acquire_token_by_device_flow(flow)

#     with open("token_cache.bin", "w") as f:
#         f.write(cache.serialize())

#     if not result:
#         print("❌ MSAL returned no result; authentication failed.")
#         print("Full result object:", result)
#         return ""                     # or raise RuntimeError

#     if "access_token" not in result:
#         print("❌ Failed to acquire token.")
#         print("Error:", result.get("error"))
#         print("Description:", result.get("error_description"))
#         print("Scopes:", scopes)
#         return ""
 
        
#     access_token = result["access_token"]
#     headers = {
#         "Authorization": f"Bearer {access_token}"
#     }
#     print("Scopes granted in token:", result.get("scope"))

#     url = make_shares_api_url(shared_onedrive_url)
#     response = requests.get(url, headers=headers)

#     if response.status_code == 200:
#         knowledge_dir = os.path.join(os.getcwd(), "knowledge")
#         os.makedirs(knowledge_dir, exist_ok=True)

#         content_disp = response.headers.get("Content-Disposition", "")
#         match = re.search(r'filename="(.+?)"', content_disp)

#         if match:
#             original_filename = match.group(1)
#             extension = os.path.splitext(original_filename)[1]
#         else:
#             extension = ""

#         new_filename = f"attachment{extension}"
#         local_file_path = os.path.join(knowledge_dir, new_filename)

#         with open(local_file_path, "wb") as f:
#             f.write(response.content)

#         print(f"✅ File downloaded and saved to: {local_file_path}")
#     else:
#         print(f"❌ Failed to download file: {response.status_code}")
#         print(response.text)

#     return new_filename
