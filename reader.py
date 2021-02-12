import os
import json
import re
import jsbeautifier
from slack_bolt import App
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import pandas as pd
import io

client = WebClient(token="xoxp-1664119445540-1643181234759-1696879914535-84e258c25d9ec7c1ecfd11f03f42cfa0")

app = App(
    token=("xoxb-1664119445540-1701240028835-15Bzsi8TbnZ7773DkBw6qi1P"),
    signing_secret=("94c1b74f6044d8382ca77173059da4eb")
)

def get_channel_message_history():
    conversation_history = []
    channel_id = "C01KC4QD951"
    try:    
        result = (client.conversations_history(channel=channel_id))
        return(result)
    except SlackApiError as e:
        print(e)

def interp_data():
    data = get_channel_message_history()
    data=data["messages"]
    # data is all slack history
    data = pd.DataFrame(data)
    # df is the important info we want
    df = data[['client_msg_id', 'type', 'text', 'user', 'ts', 'reactions']]
    # frequency gives the frequency each user speaks
    frequencies = df['user'].value_counts()

def progress_indicators():
    data = get_channel_message_history()
    data=data["messages"]
    # data is all slack history
    data = pd.DataFrame(data)
    # df is the important info we want
    df = data[['client_msg_id', 'type', 'text', 'user', 'ts', 'reactions']]

    messages = df['text']
    Progress_Messages = pd.DataFrame(columns=['Flagged'])
    finished = messages.str.contains(r'finish*', regex=True)
    for x in range(len(finished)-1):
        if finished[x]==True:
            adding = {'Flagged': messages[x]}
            Progress_Messages=Progress_Messages.append(adding, ignore_index=True)
            finished = messages.str.contains(r'finish*', regex=True)
        
    completed = messages.str.contains(r'complet*', regex=True)
    for x in range(len(completed)-1):
        if completed[x]==True:
            adding = {'Flagged': messages[x]}
            Progress_Messages=Progress_Messages.append(adding, ignore_index=True)
            completed = messages.str.contains(r'complet*', regex=True)
        
    idea = messages.str.contains(r'idea*', regex=True)
    for x in range(len(idea)-1):
        if idea[x]==True:
            adding = {'Flagged': messages[x]}
            Progress_Messages=Progress_Messages.append(adding, ignore_index=True)
            idea = messages.str.contains(r'idea*', regex=True)
        
    done = messages.str.contains(r'done*', regex=True)
    for x in range(len(done)-1):
        if done[x]==True:
            adding = {'Flagged': messages[x]}
            Progress_Messages=Progress_Messages.append(adding, ignore_index=True)
            done = messages.str.contains(r'done*', regex=True)
        
    accomplish = messages.str.contains(r'accomplish*', regex=True)
    for x in range(len(accomplish)-1):
        if accomplish[x]==True:
            adding = {'Flagged': messages[x]}
            Progress_Messages=Progress_Messages.append(adding, ignore_index=True)
            accomplish = messages.str.contains(r'accomplish*', regex=True)
        
    accquire = messages.str.contains(r'accquir*', regex=True)
    for x in range(len(accquire)-1):
        if accquire[x]==True:
            adding = {'Flagged': messages[x]}
            Progress_Messages=Progress_Messages.append(adding, ignore_index=True)
            accquire = messages.str.contains(r'accquire*', regex=True)
        
    agree = messages.str.contains(r'agree*', regex=True)
    for x in range(len(agree)-1):
        if agree[x]==True:
            adding = {'Flagged': messages[x]}
            Progress_Messages=Progress_Messages.append(adding, ignore_index=True)
            agree = messages.str.contains(r'agree*', regex=True)



