import os
import pandas as pd
from slack_bolt import App
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slacktastic.template import PieChart, Message
from slacktastic.client import SlackClient
from channel_history import on_home_opened
from googleapiclient import discovery
import json

with open('config.json') as json_file:
    data = json.load(json_file)

client = WebClient(token=os.environ.get(data["SLACK_OAUTH_TOKEN"]))
slacktastic_client = SlackClient(webhook_url=os.environ.get(data["SLACK_WEBHOOK_URL"]))
API_KEY= data["GOOGLE_API_KEY"]

app = App(
    token=os.environ.get(data["SLACK_BOT_TOKEN"]),
    signing_secret=os.environ.get(data["SLACK_SIGNING_SECRET"])
)

#Add event listeners here
@app.event("app_home_opened")
def history(say):
    on_home_opened(say)

if __name__ == "__main__":
    app.start(port=int(os.environ.get("PORT", 3000)))

# Generates API client object dynamically based on service name and version.
service = discovery.build('commentanalyzer', 'v1alpha1', developerKey=API_KEY)

analyze_request = {
  'comment': { 'text': 'friendly greetings from python' },
  'requestedAttributes': {'TOXICITY': {}}
}

response = service.comments().analyze(body=analyze_request).execute()

import json
print( json.dumps(response, indent=2))
