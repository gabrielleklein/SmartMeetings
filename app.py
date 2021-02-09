import os
import pandas as pd
from slack_bolt import App
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slacktastic.template import PieChart, Message
from slacktastic.client import SlackClient

client = WebClient(token=os.environ.get("SLACK_OAUTH_TOKEN"))
slacktastic_client = SlackClient(webhook_url=os.environ.get("SLACK_WEBHOOK_URL"))

app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)

def get_channel_message_history_as_df():
    conversation_history = []
    channel_id = "C01KC4QD951"
    try:    
        result = client.conversations_history(channel=channel_id)
        result_messages = result["messages"]
        df = pd.DataFrame(result_messages)
        return df
    except SlackApiError as e:
        print(e)

def test_data_viz():
    chart = PieChart(
        title="Test Data",
        labels=['Ride', 'Reservation'],
        values=[22,55]
    )
    return chart

#Add event listeners here
@app.event("app_home_opened")
def say_hi(say):
    text = "Hello World"
    chart = test_data_viz()
    message = Message(
        text=text,
        attachments=[chart]
    )
    slacktastic_client.send_message(message)
    #say(text)

#Don't run ./ngrok http 3000 again, it will deprecate the requests url in Slack and we will have to switch it
if __name__ == "__main__":
    app.start(port=int(os.environ.get("PORT", 3000)))
