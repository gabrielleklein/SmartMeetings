import os
from slack_bolt import App
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slacktastic.template import PieChart, Message
from slacktastic.client import SlackClient
from channel_history import on_home_opened
from googleapiclient import discovery

client = WebClient(token=os.environ.get("SLACK_OAUTH_TOKEN"))
slacktastic_client = SlackClient(webhook_url=os.environ.get("SLACK_WEBHOOK_URL"))
API_KEY=AIzaSyAVBoD5zRdkarsx5f74HSgXVZLAx6EgOks

app = App(
    token=(os.getenv('token1')),
    signing_secret=(os.getenv('token1'))
)

def get_channel_message_history():
    conversation_history = []
    channel_id = "C01KC4QD951"
    try:    
        result = client.conversations_history(channel=channel_id)
        print(result)
    except SlackApiError as e:
        print(e)

#Add event listeners here
@app.event("app_home_opened")
def say_hi(say):
    text = "Hello World"
    say(text)

#Don't run ./ngrok http 3000 again, it will deprecate the requests url in Slack and we will have to switch it
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
