import os
from slack_bolt import App
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

client = WebClient(token="xoxp-1664119445540-1643181234759-1696879914535-84e258c25d9ec7c1ecfd11f03f42cfa0")

app = App(
    token=("xoxb-1664119445540-1701240028835-15Bzsi8TbnZ7773DkBw6qi1P"),
    signing_secret=("94c1b74f6044d8382ca77173059da4eb")
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
