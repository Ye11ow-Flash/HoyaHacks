import slack
import os
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, request, Response
from slackeventsapi import SlackEventAdapter
import pyrebase

firebaseConfig = {
    'apiKey': "AIzaSyA-iQqbbopxm7gtcMzI5k-S5UPL5P56uuQ",
    'authDomain': "hgbot-6261e.firebaseapp.com",
    'databaseURL': "https://hgbot-6261e-default-rtdb.firebaseio.com",
    'projectId': "hgbot-6261e",
    'storageBucket': "hgbot-6261e.appspot.com",
    'messagingSenderId': "161839688351",
    'appId': "1:161839688351:web:af0ecfebc23afde5ce10aa",
    'measurementId': "G-RP22TSC8P1"
} # firebase configuration
firebase=pyrebase.initialize_app(firebaseConfig)
db=firebase.database()

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

app = Flask(__name__)
slack_event_adapter = SlackEventAdapter(
    os.environ.get('SIGNING_SECRET'), '/slack/events', app)

client = slack.WebClient(token=os.environ.get('SLACK_TOKEN'))
BOT_ID = client.api_call("auth.test")['user_id']

@app.route('/help',methods=['POST'])
def help():
    data = request.form
    user_id = data.get('user_id')
    channel_id = data.get('channel_id')

    if BOT_ID != user_id:
        client.chat_postMessage(channel=channel_id,text="""Commands:
                                                              /add-idea             Add an idea.
                                                              /show-idea            Show list of all ideas.
                                                              /add-feature          Add a feature.
                                                              /show-feature         Show list of all features.""")
    return Response(),200

# add-idea slash command
@app.route('/add-idea',methods=['POST'])
def add_idea():
    print("idea")
    data = request.form
    user_id = data.get('user_id')
    channel_id = data.get('channel_id')
    idea_message = data.get('text')
    user_name = data.get('user_name')
    channel_name = data.get('channel_name')

    print(request.form)

    # TODO: add the idea_message to the list of ideas on firebase db
    if db.get().val() is None or channel_name not in db.get().val(): # if new channel  
        db.child(channel_name).set({"count":1})
        db.child(channel_name).child("ideas").child(1).set({"description":idea_message})

    else:
        count=db.child(channel_name).get().val()["count"]+1
        db.child(channel_name).update({"count":count})
        db.child(channel_name).child("ideas").child(count).set({"description":idea_message})

    
    if BOT_ID != user_id:
        client.chat_postMessage(channel=channel_id,text=f"{user_name} added an Idea: {idea_message}")
    return Response(),200

# show-ideas command
@app.route('/show-ideas',methods=['POST'])
def show_ideas():
    data = request.form
    channel_id = data.get('channel_id')
    channel_name = data.get('channel_name')

    client.chat_postMessage(channel=channel_id,text=f"Showing all ideas in {channel_name}")
    i=0
    for idea in db.child(channel_name).child("ideas").get().val():
        if i>0:
            message=str(i)+". " + idea['description']
            client.chat_postMessage(channel=channel_id,text=message)
        i+=1
    return Response(),200

# add-feature command
@app.route('/add-feature',methods=['POST'])
def add_feature():
    data = request.form

    user_id = data.get('user_id')
    channel_id = data.get('channel_id')
    feature_message = data.get('text')
    user_name = data.get('user_name')
    channel_name = data.get('channel_name')


    #  retrieve data form the db
    if db.get().val() is None or channel_name not in db.get().val(): # if new channel
        db.child(channel_name).set({"count":1})
        db.child(channel_name).child("features").child(1).set({"description":feature_message})

    else:
        count=db.child(channel_name).get().val()["count"]+1
        db.child(channel_name).update({"count":count})
        db.child(channel_name).child("features").child(count).set({"description":feature_message})


    if BOT_ID != user_id:
        client.chat_postMessage(channel=channel_id,text=f"{user_name} added a Feature: {feature_message}")
    return Response(),200

if __name__ == "__main__":
    app.run(debug=True, port=3000)



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