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
slacktastic_client = SlackClient(webhook_url=os.environ.get("SLACK_WEBHOOK_URL"))
API_KEY = os.environ.get("API_KEY")
service = discovery.build('commentanalyzer', 'v1alpha1', developerKey=API_KEY)

def get_channel_message_history_as_df(oldest=0, latest=datetime.datetime.now()):
    conversation_history = []
    channel_id = "C01KC4QD951"
    try:    
        result = client.conversations_history(channel=channel_id, oldest=oldest, latest=latest)
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
    messages = messages.drop(['bot_id', 'bot_link', 'client_msg_id', 'team', 'blocks', 'files', 'upload', 'display_as_bot', 'attachments'], axis=1)
    users = users.drop(['team_id', 'color', 'tz', 'tz_label', 'tz_offset', 'profile', 'is_restricted', 'is_ultra_restricted', 'is_app_user', 'updated'], axis=1)
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

    #Perspective API
    messages.insert(6, "toxicity_score", [0] * len(messages))
    for index,row in messages.iterrows():
        try:
            analyze_request = {
                'comment': { 'text': row['text'] },
                'requestedAttributes': { 'TOXICITY': {} }
            }
            response = service.comments().analyze(body=analyze_request).execute()
            score = response['attributeScores']['TOXICITY']['spanScores'][0]['score']['value']
            messages.loc[index, "toxicity_score"] = score
            if row['user'] in toxicity_score.keys():
                toxicity_score[row['user']] += score
        except:
            messages.loc[index, "toxicity_score"] = -1
    for user in toxicity_score.keys():
        toxicity_score[user] = toxicity_score[user] / count_messages[user]
    
    return count_messages, count_reactions, id_to_real_name, activity, toxicity_score

def on_home_opened(say):
    messages = get_channel_message_history_as_df()
    users = get_users_info()
    count_messages, count_reactions, id_to_real_name, activity, toxicity_score = analyze_channel_data(messages, users)
    message_chart = PieChart(
        title="Channel Participation - Messages",
        labels=list(id_to_real_name.values()),
        values=list(count_messages.values())
    )
    reaction_chart = PieChart(
        title="Channel Participation - Reactions",
        labels=list(id_to_real_name.values()),
        values=list(count_reactions.values())
    )
    activity_chart = PieChart(
        title="Channel Activity Over the Past 4 Weeks",
        labels=["Last week", "Two weeks ago", "Three weeks ago", "Four weeks ago"],
        values=activity
    )
    toxicity_chart = BarChart(
        "Team Members' Toxicity Scores",
        labels=list(id_to_real_name.values()),
        data={
            'Toxicity Score': list(toxicity_score.values())
        }
    )
    single_message = Message(
        text="Here's historical data for channel #general",
        attachments=[message_chart, reaction_chart, activity_chart, toxicity_chart]
    )
    slacktastic_client.send_message(single_message)