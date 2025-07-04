import os
import requests
from msal import PublicClientApplication, SerializableTokenCache
from dotenv import load_dotenv
import os


def send_mail(message):
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
