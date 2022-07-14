import traceback
from slack_sdk import WebhookClient

from abn.common.constants import SLACK_WEBHOOK_URL


def notify(text: str, webhook_url: str = SLACK_WEBHOOK_URL, with_traceback: bool=False):
    """ 

    Args:
        text (str): message text.
        webhook_url (str, optional): slack webhook url.
        with_traceback (bool, optional): Defaults to False.
    """
    if with_traceback:
        text += f"\n```{traceback.format_exc()}```"

    WebhookClient(webhook_url).send(text=text)