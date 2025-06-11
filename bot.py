import slack
import os
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from .env file
#env_path = Path('') / '.env'
load_dotenv()
# Get the Slack bot token from environment variables
SLACK_BOT_TOKEN = os.getenv("SLACK_TOKEN")
# Initialize the Slack client
client = slack.WebClient(token=SLACK_BOT_TOKEN) 

client.chat_postMessage(
    channel='#test-bot',
    text='Hello, world! This is a message from your Slack bot from go.'
)
