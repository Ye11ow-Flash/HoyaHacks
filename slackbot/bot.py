from dotenv import load_dotenv
import slack 
import os 
from pathlib import Path
from dotenv import load_dotenv # pip install python-dotenv
from flask import Flask, request, Response
from slackeventsapi import SlackEventAdapter
from firebase_admin import db
import firebase_admin


firebaseConfig = {
    "apiKey": "AIzaSyA-iQqbbopxm7gtcMzI5k-S5UPL5P56uuQ",
  "authDomain": "hgbot-6261e.firebaseapp.com",
  "databaseURL": "https://hgbot-6261e-default-rtdb.firebaseio.com/",
  "projectId": "hgbot-6261e",
  "storageBucket": "hgbot-6261e.appspot.com",
  "messagingSenderId": "161839688351",
  "appId": "1:161839688351:web:af0ecfebc23afde5ce10aa",
  "measurementId": "G-RP22TSC8P1"
  
} # firebase configuration
# firebase=pyrebase.initialize_app(firebaseConfig)
# db=firebase.database()

# Firebase

cred_obj = firebase_admin.credentials.Certificate('/Users/suleymaneminov/Desktop/Winter 2022/HoyaHacks/HoyaHacks/slackbot/hgbot-6261e-firebase-adminsdk-sc4bo-5923c44976.json')
default_app = firebase_admin.initialize_app(cred_obj, {
	'databaseURL':"https://hgbot-6261e-default-rtdb.firebaseio.com/"
	})


ref = db.reference("/")
# end firebase connection config

env_path = Path('.') / '.env'

load_dotenv(dotenv_path=env_path)
 
#  flask app for web server
app = Flask(__name__)
slack_event_adapter = SlackEventAdapter(
    os.environ.get('SLACK_SIGNING_SECRET'), '/slack/events', app)

# connect to slack api
client = slack.WebClient(token=os.environ.get('SLACK_BOT_TOKEN'))
BOT_ID = client.api_call('auth.test')['user_id']


# add-idea slash command
@app.route('/add-idea',methods=['POST'])
def add_idea():
    # get data from Slack Channel
    data = request.form
    user_id = data.get('user_id')
    channel_id = data.get('channel_id')
    idea_message = data.get('text')
    user_name = data.get('user_name')

    print(idea_message)

    


    if BOT_ID != user_id:
        client.chat_postMessage(channel=channel_id,text=f"{user_name} added an Idea: {idea_message}")

        # TODO: add the idea_message to the list of ideas on firebase db
        
        #     # if db.get().val() is None or channel_id not in db.get().val(): # if new channel  
        #     #     db.child(channel_id).set({"count":1})
        #     #     db.child(channel_id).child("ideas").child(1).set({"description":idea_message})

        #     # else:
        #     #     # Save the idea on Firebase DB
        #     #     count=db.child(channel_id).get().val()["count"]+1
        #     #     db.child(channel_id).update({"count":count})
        #     #     db.child(channel_id).child("ideas").child(count).set({"description":idea_message})

        #     # Post a message to the Channel
        
        
        #     client.chat_postMessage(channel=channel_id,text=f"error occured")
        
            



        

        

    return Response(),200


# TODO: Create /show-ideas slash command - retrieve list of ideas from Firebase db ( 
#                           (e.g idea1 by user_name1 - Instagram app clone /n 
#                                idea2 by user_name2 - App that helps to sleep \n 
#                                idea3 ...  ))
# TODO: Create /create-project (title, idea-number )
#           Decide what project hackers will be working on            
# TODO: Create /add-feature command (attr={""})
#           Add feature to the list of features.
# TODO: Create /show-features 
#           Retrieve list of features from Firebase db and post message
# TODO: Create /help slash command 
#           Show list of commands 
# TODO: Create /todo slash command
#           Add to-do to list todo
# TODO: Create /assign-task slash command
# TODO: Create /show-my-tasks slash command 


if __name__ == "__main__":
    app.run(debug=True, port=3000)