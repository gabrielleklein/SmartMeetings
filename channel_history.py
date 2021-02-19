import os
import time
import json
import datetime
import pandas as pd
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slacktastic.template import PieChart, Message, BarChart
from slacktastic.client import SlackClient
from googleapiclient import discovery
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
client = WebClient(token=os.environ.get("SLACK_OAUTH_TOKEN"))
slacktastic_client = SlackClient(webhook_url=os.environ.get("SLACK_WEBHOOK_URL_APP"))
API_KEY = os.environ.get("API_KEY")
service = discovery.build('commentanalyzer', 'v1alpha1', developerKey=API_KEY)

def get_channel_message_history_as_df(oldest=0, latest=datetime.datetime.now()):
    conversation_history = []
    channel_id = "C01KC4QD951"
    try:    
        result = client.conversations_history(channel=channel_id, oldest=oldest, latest=latest, limit=1000)
        result_messages = result["messages"]
        df = pd.DataFrame(result_messages)
        return df
    except SlackApiError as e:
        print(e)

def get_users_info():
    users = client.users_list()
    users_results = users['members']
    df = pd.DataFrame(users_results)
    return df

def analyze_channel_data(messages, users):
    #Message + reaction frequency
    users_filtered = users[users['is_bot'] == False]
    users_filtered.insert(10, "messages_sent", [0,0,0,0,0])
    users_filtered.insert(11, "reactions_sent", [0,0,0,0,0])
    users_filtered.insert(12, "toxicity_score", [0,0,0,0,0])
    count_messages = dict(zip(users_filtered.id, users_filtered.messages_sent))
    count_reactions = dict(zip(users_filtered.id, users_filtered.reactions_sent))
    toxicity_score = dict(zip(users_filtered.id, users_filtered.toxicity_score))
    id_to_real_name = dict(zip(users_filtered.id, users_filtered.real_name))
    for index,row in messages.iterrows():
        if row['user'] in count_messages.keys():
            count_messages[row['user']] += 1
            if type(row['reactions']) == list:
                count_reactions[row['user']] += 1

    #Overall Activity
    delta = datetime.timedelta(days=7)
    today = datetime.datetime.now()
    today_ts = datetime.datetime.timestamp(today)
    one_week_ts = datetime.datetime.timestamp(today - delta)
    two_week_ts = datetime.datetime.timestamp(today - (2 * delta))
    three_week_ts = datetime.datetime.timestamp(today - (3 * delta))
    four_week_ts = datetime.datetime.timestamp(today - (4 * delta))
    one_week_msg_count = len(get_channel_message_history_as_df(oldest=one_week_ts, latest=today_ts))
    two_week_msg_count = len(get_channel_message_history_as_df(oldest=two_week_ts, latest=one_week_ts))
    three_week_msg_count = len(get_channel_message_history_as_df(oldest=three_week_ts, latest=two_week_ts))
    four_week_msg_count = len(get_channel_message_history_as_df(oldest=four_week_ts, latest=three_week_ts))
    activity = [one_week_msg_count, two_week_msg_count, three_week_msg_count, four_week_msg_count]
    return count_messages, count_reactions, id_to_real_name, activity, toxicity_score, messages

def analyze_toxicity(messages, id_to_real_name, toxicity_score, count_messages):
    #Perspective API
    #cut_messages = messages.head(50) #Only get most recent 50 messages to stay below limit for now
    for index,row in messages.iterrows():
        if row['user'] in toxicity_score.keys():
                toxicity_score[row['user']] += row['toxicity_score']

    for user in toxicity_score.keys():
        if count_messages[user] > 0:
            toxicity_score[user] = toxicity_score[user] / count_messages[user]

    return toxicity_score

def message_history():
    messages = pd.read_csv("messages_history.csv")
    users = get_users_info()
    count_messages, count_reactions, id_to_real_name, activity, toxicity_score, messages = analyze_channel_data(messages, users)
    message_chart = PieChart(
        title="Channel Participation - Messages",
        labels=list(id_to_real_name.values()),
        values=list(count_messages.values())
    )
    message = Message(
        text="Historical message data for channel #general",
        attachments=[message_chart]
    )
    slacktastic_client.send_message(message)

def reaction_history():
    messages = get_channel_message_history_as_df()
    users = get_users_info()
    count_messages, count_reactions, id_to_real_name, activity, toxicity_score, messages = analyze_channel_data(messages, users)
    reaction_chart = PieChart(
        title="Channel Participation - Reactions",
        labels=list(id_to_real_name.values()),
        values=list(count_reactions.values())
    )
    message = Message(
        text="Historical reaction data for channel #general",
        attachments=[reaction_chart]
    )
    slacktastic_client.send_message(message)

def activity():
    messages = pd.read_csv("messages_history.csv")
    users = get_users_info()
    count_messages, count_reactions, id_to_real_name, activity, toxicity_score, messages = analyze_channel_data(messages, users)
    activity_chart = PieChart(
        title="Channel Activity Over the Past 4 Weeks",
        labels=["Last week", "Two weeks ago", "Three weeks ago", "Four weeks ago"],
        values=activity
    )
    message = Message(
        text="Overall activity data for channel #general",
        attachments=[activity_chart]
    )
    slacktastic_client.send_message(message)

def toxicity_history():
    messages = pd.read_csv("messages_history.csv")
    users = get_users_info()
    count_messages, count_reactions, id_to_real_name, activity, toxicity_score, messages = analyze_channel_data(messages, users)
    toxic = analyze_toxicity(messages, id_to_real_name, toxicity_score, count_messages)
    toxicity_chart = BarChart(
        "Team Members' Toxicity Scores",
        labels=list(id_to_real_name.values()),
        data={
            'Toxicity Score': list(toxic.values())
        }
    )
    message = Message(
        text="Channel toxicity data for channel #general",
        attachments=[toxicity_chart]
    )
    slacktastic_client.send_message(message)

#This has to get entire message history so as to update from messages when the app wasn't running
def update_messages(event, say):
    if event['channel'] == "C01KC4QD951":
        old = pd.read_csv("messages_history.csv")
        new = get_channel_message_history_as_df()
        #new.insert(len(new.columns), 'toxicity_score', [0] * len(new))
        diff = len(new) - len(old)
        if diff > 0:
            diff_rows = new.loc[:diff-1]
            frames = [diff_rows, old]
            result = pd.concat(frames, ignore_index=True)
            for index,row in diff_rows.iterrows():
                try:
                    analyze_request = {
                        'comment': { 'text': row['text'] },
                        'requestedAttributes': { 'TOXICITY': {} }
                    }
                    response = service.comments().analyze(body=analyze_request).execute()
                    score = response['attributeScores']['TOXICITY']['spanScores'][0]['score']['value']
                    result.loc[index, "toxicity_score"] = score
                except:
                    result.loc[index, "toxicity_score"] = 0
            #Remove added columns
            cols_to_rm = [ele for ele in result.columns if 'Unnamed' in ele]
            result = result.drop(cols_to_rm, axis=1)
            result.to_csv("messages_history.csv")
            #Signal done
            done = Message(
                text="Updated DB!",
                attachments=[]
            )
            slacktastic_client.send_message(done)
