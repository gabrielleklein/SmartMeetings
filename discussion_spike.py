import time
import datetime
import os
import copy
from dotenv import load_dotenv, find_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

load_dotenv(find_dotenv())
client = WebClient(token=os.environ.get("SLACK_BOT_TOKEN"))

message_prompt = "Looks like the channel's filled with busy bees. How about adding to the buzz?"
# number of messages to determine a discussion
discussion_thresh = 3
# how long we're defining a discussion in terms of hours
delta = datetime.timedelta(minutes=30)
now = datetime.datetime.now()

# creates an array of conversation members, which will keep track of who needs to be prompted
def make_member_array(channel_id):
    result = client.conversations_members(channel=channel_id)
    return result['members'][:4]

# creates an array of conversation messages
def make_messages_array(channel_id, latest, oldest):
    result = client.conversations_history(channel=channel_id, latest=latest, oldest=oldest)
    return result['messages']

# checks if a the discussion threshold has been reached within the period
def is_discussion(channel_id, quiet_members):
    oldest = datetime.datetime.timestamp(now - delta)

    # disc_messages is a list object of messages from the discussion
    disc_messages = make_messages_array(channel_id, now, oldest)
    # members is a list object of users
    members = make_member_array(channel_id)
    
    # counts only messages sent by users (excludes bot messages)
    count_messages = 0
    for message in disc_messages:
        for i in range(len(members)):
            try:
                if message['user'] == members[i]:
                    count_messages = count_messages + 1
                    quiet_members[i] = False
                # removes group member that sent message from quiet members 
            except:
                print("This is a bot message")
    return count_messages >= discussion_thresh, quiet_members

# checks to see if a discussion prompt has already been sent within two discussion periods
def is_prompt_sent(channel_id):
    oldest = datetime.datetime.timestamp(now - 2 * delta)

    messages = make_messages_array(channel_id, now, oldest) 
    for message in messages:
        if message['text'] == message_prompt:
            return True
    return False

# encourages users who have not participated in two discussion periods to participate in a discussion
# encourages the last person to send a message too
def encourage_participation(event, say):
    channel_id = event['channel']
    quiet_members = make_member_array(channel_id)
    is_disc, quiet = is_discussion(channel_id, quiet_members)
    if (is_disc and not is_prompt_sent(channel_id)):
        for member in quiet:
            if member:
                client.chat_postEphemeral(
                    channel=channel_id,
                    text=message_prompt,
                    user=member
                )
