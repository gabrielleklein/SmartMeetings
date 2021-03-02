import os
import re
from googleapiclient import discovery
from dotenv import load_dotenv, find_dotenv
from slack_sdk import WebClient

load_dotenv(find_dotenv())
API_KEY = os.environ.get("API_KEY")
service = discovery.build('commentanalyzer', 'v1alpha1', developerKey=API_KEY)
client = WebClient(token=os.environ.get("SLACK_BOT_TOKEN"))

def flag_toxic_message(event, say):
    try:
        analyze_request = {
            'comment': { 'text':event['text'] },
            'requestedAttributes': { 'TOXICITY':{} }
        }
        response = service.comments().analyze(body=analyze_request).execute()
        score = response['attributeScores']['TOXICITY']['spanScores'][0]['score']['value']
        if score > 0.75:
            client.chat_postEphemeral(
                channel=event['channel'],
                text="The helpWe algorithm flagged your last message for toxicity, and we wanted to bring it to your attention.",
                user=event['user']
            )
    except:
        print("Whoops! Looks like we reached our request limit...")

def flag_progress_message(event, say):
    to_send = "It seems like the team has made some progress, send them some encouragement!"
    if (event['type'] == "message"):
        if (re.search((r'agree*'), event['text'])):
            client.chat_postMessage(
                channel=event['channel'],
                text=to_send
            )
        if(re.search((r'complet*'), event['text'])):
            client.chat_postMessage(
                channel=event['channel'],
                text=to_send
            )
        if (re.search((r'finish*'), event['text'])):
            client.chat_postMessage(
                channel=event['channel'],
                text=to_send
            )
        if (re.search((r'idea*'), event['text'])):
            client.chat_postMessage(
                channel=event['channel'],
                text=to_send
            )
        if (re.search((r'done*'), event['text'])):
            client.chat_postMessage(
                channel=event['channel'],
                text=to_send
            )
        if (re.search((r'accomplish*'), event['text'])):
            client.chat_postMessage(
                channel=event['channel'],
                text=to_send
            )
        if (re.search((r'accquir*'), event['text'])):
            client.chat_postMessage(
                channel=event['channel'],
                text=to_send
            )
        if (re.search((r'push*'), event['text'])):
            client.chat_postMessage(
                channel=event['channel'],
                text=to_send
            )
