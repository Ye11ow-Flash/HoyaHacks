from dotenv import load_dotenv
import slack 
import os 
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, request, Response
from slackeventsapi import SlackEventAdapter
import pyrebase # pip install pyrebase

firebaseConfig = {
  
} # firebase configuration
firebase=pyrebase.initialize_app(firebaseConfig)
db=firebase.database()

env_path = Path('.') / '.env'

load_dotenv(dotenv_path=env_path)
 
app = Flask(__name__)
slack_event_adapter = SlackEventAdapter(
    os.environ.get('SLACK_SIGNING_SECRET'), '/slack/events', app)

# connect to slack api
client = slack.WebClient(token=os.environ.get('SLACK_BOT_TOKEN'))
BOT_ID = client.api_call('auth.test')['user_id']

# # message responder
# @slack_event_adapter.on('message')
# def message(payload):
#     event = payload('event', {})
#     channel_id = event.get('channel')
#     user_id = event.get('user')
#     text = event.get('text')

#     if BOT_ID != user_id:
#         client.chat_postMessage(channel=channel_id,text=text)


# add-idea slash command
@app.route('/add-idea',methods=['POST'])
def add_idea():
    data = request.form
    user_id = data.get('user_id')
    channel_id = data.get('channel_id')
    idea_message = data.get('text')
    user_name = data.get('user_name')

    print(request.form)

    # TODO: add the idea_message to the list of ideas on firebase db
    if db.get().val() is None or channel_id not in db.get().val(): # if new channel  
        db.child(channel_id).set({"count":1})
        db.child(channel_id).child("ideas").child(1).set({"description":idea_message})

    else:
        count=db.child(channel_id).get().val()["count"]+1
        db.child(channel_id).update({"count":count})
        db.child(channel_id).child("ideas").child(count).set({"description":idea_message})

    
    if BOT_ID != user_id:

        client.chat_postMessage(channel=channel_id,text=f"{user_name} added an Idea: {idea_message}")

    return Response(),200


if __name__ == "__main__":
    app.run(debug=True, port=3000)