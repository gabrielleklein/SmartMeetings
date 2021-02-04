import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

client = WebClient(token="xoxp-1664119445540-1643181234759-1711827738771-d918ffb1c4aba0acb1953228da09f34f")

conversation_history = []
channel_id = "C01KC4QD951"

try:
    result = client.conversations_history(channel=channel_id)
    print(result)
except SlackApiError as e:
    print(f"Error creating conversation: {e}")