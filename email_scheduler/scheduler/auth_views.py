# scheduler/auth_views.py

import os
from django.shortcuts import redirect
from msal import ConfidentialClientApplication

def authorize(request):
    client_id     = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")
    authority     = os.getenv("AUTHORITY")
    redirect_uri  = request.build_absolute_uri(os.getenv("REDIRECT_PATH"))
    scopes        = os.getenv("SCOPES").split()

    app = ConfidentialClientApplication(
        client_id, authority=authority, client_credential=client_secret
    )

    auth_url = app.get_authorization_request_url(
        scopes,
        redirect_uri=redirect_uri,
        response_mode="query",
        prompt="select_account",
    )
    return redirect(auth_url)

# scheduler/auth_views.py (continued)

import os, json
from django.shortcuts import redirect
from django.http import HttpResponse
from msal import ConfidentialClientApplication, SerializableTokenCache

def callback(request):
    code = request.GET.get("code")
    if not code:
        return HttpResponse("Error: No code returned", status=400)

    client_id     = os.getenv("CLIENT_ID")
    client_secret = os.getenv("CLIENT_SECRET")
    authority     = os.getenv("AUTHORITY")
    redirect_uri  = request.build_absolute_uri(os.getenv("REDIRECT_PATH"))
    scopes        = os.getenv("SCOPES").split()

    cache = SerializableTokenCache()
    app   = ConfidentialClientApplication(
        client_id, authority=authority, client_credential=client_secret,
        token_cache=cache
    )

    result = app.acquire_token_by_authorization_code(
        code,
        scopes=scopes,
        redirect_uri=redirect_uri,
    )
    if "access_token" not in result:
        return HttpResponse(f"Token error: {result.get('error_description')}", status=400)

    # Persist the cache to a file (or database)
    with open("token_cache.bin", "w") as f:
        f.write(cache.serialize())

    return redirect("/")  # back to your scheduler page
