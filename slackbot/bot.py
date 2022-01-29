from dotenv import load_dotenv
import slack 
import os 
from pathlib import Path
from dotenv import load_dotenv

env_path = Path('.') / '.env'

load_dotenv(dotenv_path=env_path)

client = slack.WebClient(token=os.environ.get('SLACK_BOT_TOKEN'))

client.chat_postMessage(channel='#hackathon-project',text='Sup My G!')
