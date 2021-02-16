import json
import logging

import requests

from slacktastic.template import Message


class SlackClient:
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url
        self.logger = logging.getLogger(__name__)

    def send_message(self, message: Message):
        payload = json.dumps(message.to_slack())
        response = requests.post(self.webhook_url, data=[('payload', payload)])

        if not response.ok:
            self.logger.critical(
                f'Could not post statistics to Slack: {response.text}')
