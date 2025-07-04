import os
import base64
import requests
from msal import PublicClientApplication, SerializableTokenCache
from dotenv import load_dotenv
import os

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
        # message["message"]["attachments"] = [
        #         attach_attachment(file_name)
        #     ]
        
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



# syntax = {
#         "message": {
#             "subject": "Subject Goes Here",
#             "body": {
#                 "contentType": "Text",
#                 "content": "all the content of the mail"
#             },

#             "attachments": [
#                 attach_attachment("document.txt")
#             ],

#             "toRecipients": [
#                 {
#                     "emailAddress": {
#                         "address": "i220792@nu.edu.pk"
#                     }
#                 }
#             ]
#         },
#         "saveToSentItems": "true"
#     }

# message = {
#     "message": {
#         "subject": "CrewAI Email Sender Implementation Complete",
#         "body": {
#         "contentType": "Text",
#         "content": "all the content of the mail"
#         },

#         "toRecipients": [
#         {
#             "emailAddress": {
#             "address": "i220792@nu.edu.pk"
#             }
#         }
#         ]		
#     }
# }


# message["message"]["attachments"] = [
#             attach_attachment("document.txt")
#         ]

# import pprint
# pprint.pprint(syntax)
# print("\n---------------------------------------------------------------------\n")
# pprint.pprint(message)


# # print(message)
# send_mail(message)

# def okko():
#     return "OKOK")

# message ["mahad"] = [
#             okko()
#         ],
# print("okok\n\n",message)
