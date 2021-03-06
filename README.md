# SmartMeetings
CS 338 - Smart Meetings Slack

## Slack Client Actions
The Slack client from the Slack SDK let's us perform static operations in our workspace,
i.e. get channel's history at that point in time, send a message, etc.
https://slack.dev/python-slack-sdk/index.html

## Event Subscriptions
Using the Slack Bolt features we can listen to realtime events in our app, such as messages sent,
messages received, app home screen opened, etc. https://slack.dev/bolt-python/tutorial/getting-started

To do this, add an event subscription here https://api.slack.com/apps/A01LT5D4T7E/event-subscriptions?,
(add bot user event) then add the respective listener (in docs above) into app.py, run the script, and test in Slack.

## Setup & Running
Run ./ngrok http 3000 and leave it running, copy the forwarding URL into the event-subscriptions, slash commands, and
shortcuts (see below), then run app.py.

Event subscriptions: https://api.slack.com/apps/A01LT5D4T7E/event-subscriptions?  
Slash commands: https://api.slack.com/apps/A01LT5D4T7E/slash-commands?  
Shortcuts: https://api.slack.com/apps/A01LT5D4T7E/interactive-messages?

## Authorization Tokens
OAuth Token & Bot Token here: https://api.slack.com/apps/A01LT5D4T7E/oauth?  
Signing Secret here: https://api.slack.com/apps/A01LT5D4T7E/general?  
Webhook Url here: https://api.slack.com/apps/A01LT5D4T7E/incoming-webhooks?success=1
