import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

client = WebClient(token="xoxb-1664119445540-1701240028835-rtuykxw8fdfFl0JbBxLvOmDh")

conversation_history = []
channel_id = "C01KC4QD951"

try:
    result = client.conversations_history(channel=channel_id)
    print(result)
except SlackApiError as e:
    print(f"Error creating conversation: {e}")