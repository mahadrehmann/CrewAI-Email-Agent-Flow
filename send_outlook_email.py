import os
import base64
import requests
from msal import PublicClientApplication, SerializableTokenCache
from dotenv import load_dotenv
import re
from docx import Document
from PyPDF2 import PdfReader

def convert_to_txt(input_path: str, output_dir: str = "knowledge") -> str:
    """Converts .docx or .pdf file to .txt, returns path to .txt file."""
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
        return input_path  # Already text
    else:
        raise ValueError(f"Unsupported file type: {ext}")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)

    return output_path

def attach_attachment(file_path):
    if not os.path.exists(file_path):
        print('file not found')
        return
    
    with open(file_path, 'rb') as upload:
        media_content = base64.b64encode(upload.read())

    data_body = {
        '@odata.type': '#microsoft.graph.fileAttachment',
        'contentBytes': media_content.decode('utf-8'),
        'name': os.path.basename(file_path)
    }
    return data_body


def send_mail(message, file_name=""):
    
    load_dotenv()

    client_id = os.getenv("CLIENT_ID")
    # tenant_id = os.getenv("TENANT_ID")
    authority = os.getenv("AUTHORITY")
    scopes = os.getenv("SCOPES", "").split()

    # Initialize cache
    cache = SerializableTokenCache()
    if os.path.exists("token_cache.bin"):
        cache.deserialize(open("token_cache.bin", "r").read())

    # Initialize MSAL app with cache
    app = PublicClientApplication(
        client_id=client_id,
        authority=authority,
        token_cache=cache
    )

    # Try silent login
    accounts = app.get_accounts()
    if accounts:
        result = app.acquire_token_silent(scopes, account=accounts[0])
    else:
        # Fallback to device flow login
        flow = app.initiate_device_flow(scopes=scopes)
        if "user_code" not in flow:
            raise Exception("Failed to create device flow")
        print(f"\nPlease go to {flow['verification_uri']} and enter the code: {flow['user_code']}\n")
        result = app.acquire_token_by_device_flow(flow)

    # Save token cache to file
    with open("token_cache.bin", "w") as f:
        f.write(cache.serialize())

    # Proceed if token acquired
    print("Scopes in token:", result.get("scope"))
    if "access_token" in result:
        access_token = result["access_token"]
        print("✅ Access token acquired.")

        # Get the logged-in user's email
        user_info = requests.get(
            "https://graph.microsoft.com/v1.0/me",
            headers={"Authorization": f"Bearer {access_token}"}
        ).json()
        user_email = user_info.get("mail") or user_info.get("userPrincipalName")
        print(f"📧 Logged in as: {user_email}")

        # if file is not empty, do this:
        if file_name != "":
            message["message"]["attachments"] = [
                attach_attachment(file_name)
            ]
        
        print("\n\n--------SENDING THIS:\n", message)
        # Send email
        send_response = requests.post(
            "https://graph.microsoft.com/v1.0/me/sendMail",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            },
            json=message
        )

        if send_response.status_code == 202:
            print("✅ Email sent successfully!")
        else:
            print(f"❌ Failed to send email: {send_response.status_code}\n{send_response.text}")
    else:
        print("❌ Failed to acquire token:", result.get("error_description"))



def download_file_from_onedrive(one_drive_file_path):
    load_dotenv()

    client_id = os.getenv("CLIENT_ID")
    authority = os.getenv("AUTHORITY")
    scopes = os.getenv("SCOPES", "").split()

    cache = SerializableTokenCache()
    if os.path.exists("token_cache.bin"):
        cache.deserialize(open("token_cache.bin", "r").read())

    app = PublicClientApplication(client_id=client_id, authority=authority, token_cache=cache)

    accounts = app.get_accounts()
    if accounts:
        result = app.acquire_token_silent(scopes, account=accounts[0])
    else:
        flow = app.initiate_device_flow(scopes=scopes)
        print(f"Please go to {flow['verification_uri']} and enter the code: {flow['user_code']}")
        result = app.acquire_token_by_device_flow(flow)

    with open("token_cache.bin", "w") as f:
        f.write(cache.serialize())

    if "access_token" in result:
        access_token = result["access_token"]
        headers = {
            "Authorization": f"Bearer {access_token}"
        }

        print("Scopes granted in token:", result.get("scope"))

        onedrive_file_path = one_drive_file_path

        # Construct URL
        url = f"https://graph.microsoft.com/v1.0/me/drive/root:{onedrive_file_path}:/content"

        # Download the file content
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            # Ensure the folder exists
            knowledge_dir = os.path.join(os.getcwd(), "knowledge")
            os.makedirs(knowledge_dir, exist_ok=True)

            # Try to get original filename from the response header
            content_disp = response.headers.get("Content-Disposition", "")
            match = re.search(r'filename="(.+?)"', content_disp)

            if match:
                original_filename = match.group(1)
                extension = os.path.splitext(original_filename)[1]  # e.g., '.pdf', '.txt'
            else:
                extension = ""  # fallback if no filename in headers

            # Set the full path with the new filename while keeping original extension
            new_filename = f"attachment{extension}"
            local_file_path = os.path.join(knowledge_dir, new_filename)

            # Save the file
            with open(local_file_path, "wb") as f:
                f.write(response.content)

            print(f"✅ File downloaded and saved to: {local_file_path}")
        else:
            print(f"❌ Failed to download file: {response.status_code}")
            print(response.text)


    else:
        print("❌ Failed to authenticate:", result.get("error_description"))

    return new_filename

# print("\n------------------------------\nbismillah\n")     
# this = download_file_from_onedrive()   
# print("the file is", this)