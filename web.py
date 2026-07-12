from libraries import paths
from flask import Flask, request, redirect, render_template, url_for
from google_auth_oauthlib.flow import Flow, InstalledAppFlow
from libraries.user import Handler

app = Flask("Bearlander")

class OAuthClient:
    def __init__(self):
        #initialise client by loading server side credentials
        def load_credentials():
            import json
            with open(f"{paths.get_StaticsPath()}/clientCredentials.json", "r") as file: data = json.load(file)
            return data

        self._callback_url = "http://127.0.0.1:5000/callback" 
        self._client_id = load_credentials()[0]["clientID"]
        self._client_secret = load_credentials()[0]["clientSecret"]
        self._scopes = ["https://www.googleapis.com/auth/calendar"]

        self._client_config = {
            "web": {
                "client_id": self._client_id,
                "client_secret": self._client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        }

    def get_flow(self): 
        """Returns Google Flow""" 
        return Flow.from_client_config(
            self._client_config, self._scopes, redirect_uri=self._callback_url
        )
    
    def get_auth_url(self):
        flow = self.get_flow()
        auth_url, _ = flow.authorization_url(access_type="offline", include_granted_scopes="true", prompt="consent")
        
        return auth_url #uses flow inbuilt function to return url
    
    def get_credentials(self, code): #code is passed from request in Flask application
        flow = self.get_flow()
        flow.fetch_token(code=code)

        return flow.credentials

@app.route("/auth")
def auth():
    client = OAuthClient()
    auth_url = client.get_auth_url()
    return redirect(auth_url) #redirects to authentication page by google

@app.route("/callback", methods=["POST", "GET"]) #after authentication by google, returns to callback function 
def callback(): 
    client = OAuthClient()
    credentials = client.get_credentials(code=request.args.get("code")) #returns a credentials object

    final = { #example
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": credentials.scopes,
    }

    #update user credentials
    user = Handler("jaydsoh@gmail.com", "pYTHON101").login()
    user.update_credentials(credentials)

    return final

    
@app.route("/", methods=["GET", "POST"])
def home():
    return render_template("home.html")

@app.route("/features", methods=["GET", "POST"])
def features():
    return None

@app.route("/subject-rep-payment", methods=["GET", "POST"])
def payment():
    return None

@app.route("/notes", methods=["GET", "POST"])
def notes():
    return None

@app.route("/help-documentation", methods=["GET", "POST"])
def help_documentation():
    return None

if __name__ == "__main__":
    app.run()

