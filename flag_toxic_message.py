import os
from googleapiclient import discovery

API_KEY = os.environ.get("API_KEY")
service = discovery.build('commentanalyzer', 'v1alpha1', developerKey=API_KEY)

def flag_toxic_message(event, say):
    analyze_request = {
        'comment': { 'text':event['text'] },
        'requestedAttributes': { 'TOXICITY':{} }
    }
    response = service.comments().analyze(body=analyze_request).execute()
    score = response['attributeScores']['TOXICITY']['spanScores'][0]['score']['value']
    say(str(score))
    if score > 0.5:
        say("The helpWe algorithm flagged your last message for toxicity, and we wanted to bring it to your attention.")