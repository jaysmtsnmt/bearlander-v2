from flask import Flask, redirect, render_template, url_for
from google_auth_oauthlib.flow import Flow
from flask import request

app = Flask(__name__)

# this callback URL should match one saved in GCP app console "Authorized redirection URIs" section 
CALLBACK_URL = "http://127.0.0.1:5000/callback" # you can use `url_for('callback')` instead
API_CLIENT_ID = ""
API_CLIENT_SECRET = ""
SCOPES = ["https://www.googleapis.com/auth/calendar"] #scopes to pass to calendar

class CalendarClient:
    API_SERVICE = "calendar"
    API_VERSION = "v3"

    def __init__(self, client_id: str, client_secret: str, scopes: list[str]):
        self._client_id = client_id
        self._client_secret = client_secret
        self._scopes = scopes
        self._client_config = {
            "web": {
                "client_id": client_id,
                "client_secret": client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        }

    def get_flow(self, callback_url: str):
        return Flow.from_client_config(
            self._client_config, self._scopes, redirect_uri=callback_url
        )

    def get_auth_url(self, callback_url: str):
        flow = self.get_flow(callback_url)
        auth_url, _ = flow.authorization_url(
            access_type="offline", include_granted_scopes="true"
        )
        return auth_url

    def get_credentials(self, code: str, callback_url: str):
        flow = self.get_flow(callback_url)
        flow.fetch_token(code=code)
        return flow.credentials

@app.route("/callback")
def callback():
    client = CalendarClient(API_CLIENT_ID, API_CLIENT_SECRET, SCOPES)

    credentials = client.get_credentials(
        code=request.args.get("code"),
        callback_url=CALLBACK_URL,
    )
    
    final = {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": credentials.scopes,
    }

    print(final)



@app.route("/auth")
def auth():
    client = CalendarClient(API_CLIENT_ID, API_CLIENT_SECRET, SCOPES)
    auth_url = client.get_auth_url(CALLBACK_URL)
    print(auth_url)
    return redirect(auth_url)


if __name__ == "__main__":
    app.run()