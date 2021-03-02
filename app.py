import os
from dotenv import load_dotenv, find_dotenv
import pandas as pd
from slack_bolt import App
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slacktastic.template import PieChart, Message
from slacktastic.client import SlackClient
from channel_history import message_history, reaction_history, activity, toxicity_history, update_messages, toxic_messages_sent
from flag_messages import flag_toxic_message, flag_progress_message
from discussion_spike import encourage_participation

load_dotenv(find_dotenv())

app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)

#Add event listeners here
#@app.event("app_home_opened")
#def update(say):
#    say("Hello from helpWe!")

@app.event("message")
def flag(event, say):
    update_messages(event, say)
    flag_toxic_message(event, say)
    flag_progress_message(event, say)
    #encourage_participation(event, say)

@app.command("/message_history")
def m_command(ack, say, command):
    ack()
    say("Gathering data on your team's message history...")
    message_history()

@app.command("/reaction_history")
def r_command(ack, say, command):
    ack()
    say("Gathering data on your team's reaction history...")
    reaction_history()

@app.command("/activity")
def a_command(ack, say, command):
    ack()
    say("Gathering data on your team's activity...")
    activity()

@app.command("/toxicity_scores")
def t_command(ack, say, command):
    ack()
    say("Gathering data on your team's toxicity...")
    toxicity_history()

@app.command("/toxic_messages_sent")
def ts_command(ack, say, command):
    ack()
    say("Gathering data on your team's toxicity...")
    toxic_messages_sent()

@app.shortcut("messages_shortcut")
def m_shortcut(ack, shortcut, client):
    ack()
    message_history()    

@app.shortcut("reaction_shortcut")
def r_shortcut(ack, shortcut, client):
    ack()
    reaction_history()

@app.shortcut("activity_shortcut")
def a_shortcut(ack, shortcut, client):
    ack()
    activity()

@app.shortcut("toxicity_shortcut")
def t_shortcut(ack, shortcut, client):
    ack()
    toxicity_history()

@app.shortcut("toxic_messages_sent")
def ts_shortcut(ack, shortcut, client):
    ack()
    toxic_messages_sent()

if __name__ == "__main__":
    app.start(port=int(os.environ.get("PORT", 3000)))