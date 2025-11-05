# pip install google-auth-oauthlib google-auth
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES)
creds = flow.run_local_server(port=0)

with open("token.json", "w") as f:
    f.write(creds.to_json())

print("REFRESH_TOKEN=", creds.refresh_token)
print("CLIENT_ID=", creds.client_id)
print("CLIENT_SECRET=", creds.client_secret)
