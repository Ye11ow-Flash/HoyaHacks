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
                                                              /add-idea                  Add an idea.
                                                              /show-ideas             Show list of all ideas.
                                                              /add-feature            Add a feature.
                                                              /show-features       Show list of all features.
                                                              /_clear                      Clear the list for channel.
                                                              /todo                        Add a todo task to a todo list
                                                              /show-todo-list       Show list of all tasks in todo list""")
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
    if db.get().val() is None or channel_name not in db.get().val() or (db.child(channel_name).child('ideas').child("count").get().val() is None) : # if new channel  
        db.child(channel_name).child('ideas').set({"count":1})
        db.child(channel_name).child("ideas").child(1).set({"description":idea_message})

    else:
        count=db.child(channel_name).child('ideas').get().val()["count"]+1
        db.child(channel_name).child('ideas').update({"count":count})
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

    i = db.child(channel_name).child('ideas').child("count").get().val()
    message = f"Showing all ideas in {channel_name}: \n"
    
    for j in range(1, i+1):       
        message+=str(j) +'. ' + (str(db.child(channel_name).child("ideas").child(str(j)).child('description').get().val())) + '\n'
        j = j+1
        # if i>0:
        #     # message+=str(i)+". " + idea['description'] + '\n'
        #     print("IDEA::" + idea)
        # i+=1
    client.chat_postMessage(channel=channel_id,text=message)
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
    if db.get().val() is None or channel_name not in db.get().val() or (db.child(channel_name).child('features').child("feature-count").get().val() is None): # if new channel
        db.child(channel_name).child('features').set({"feature-count":1})
        db.child(channel_name).child("features").child(1).set({"description":feature_message})

    else:
        count=db.child(channel_name).child('features').get().val()["feature-count"]+1
        db.child(channel_name).child('features').update({"feature-count":count})
        db.child(channel_name).child("features").child(count).set({"description":feature_message})


    if BOT_ID != user_id:
        client.chat_postMessage(channel=channel_id,text=f"{user_name} added a Feature: {feature_message}")
    return Response(),200



# show-features command
@app.route('/show-features',methods=['POST'])
def show_features():
    data = request.form
    channel_id = data.get('channel_id')
    channel_name = data.get('channel_name')

    i=db.child(channel_name).child('features').child("feature-count").get().val()
    message = f"Showing all features in {channel_name}: \n"
    for j in range(1, i+1):
        message+=str(j) +'. ' + (str(db.child(channel_name).child("features").child(str(j)).child('description').get().val())) + '\n'
        j+=1
    client.chat_postMessage(channel=channel_id,text=message)
    return Response(),200

# clear command
@app.route('/_clear',methods=['POST'])
def clear():
    data=request.form
    channel_name=data.get('channel_name')
    db.child(channel_name).remove()
    return Response(),200


# todo command - add todo to db
@app.route('/todo',methods=['POST'])
def todo():
    data = request.form
    user_id = data.get('user_id')
    channel_id = data.get('channel_id')
    todo_message = data.get('text')
    user_name = data.get('user_name')
    channel_name = data.get('channel_name')


    #  retrieve data form the db
    if db.get().val() is None or channel_name not in db.get().val() or (db.child(channel_name).child('todo-list').child("todo-count").get().val() is None): # if new channel
        db.child(channel_name).child('todo-list').set({"todo-count":1})
        db.child(channel_name).child("todo-list").child(1).set({
            "description":todo_message,
            "author-id":user_id,
            "author-name":user_name})
        
        

    else:
        count=db.child(channel_name).child('todo-list').get().val()["todo-count"]+1
        db.child(channel_name).child('todo-list').update({"todo-count":count})
        db.child(channel_name).child("todo-list").child(count).set({
            "description":todo_message,
            "author-id":user_id,
            "author-name":user_name})


    if BOT_ID != user_id:
        client.chat_postMessage(channel=channel_id,text=f"{user_name} added a todo: {todo_message}")
    return Response(),200
    # show-todo-list = show list of todo's
    # /remove-todo 

@app.route('/show-todo-list',methods=['POST'])
def show_todo_list():
    # request data
    data = request.form
    user_id = data.get('user_id')
    channel_id = data.get('channel_id')
    todo_message = data.get('text')
    user_name = data.get('user_name')
    channel_name = data.get('channel_name')


    i=db.child(channel_name).child('todo-list').child("todo-count").get().val()
    message = f"Showing all todo in {channel_name}: \n"
    for j in range(1, i+1):
        message+=str(j) +'. ' + (str(db.child(channel_name).child("todo-list").child(str(j)).child('description').get().val())) + '\n'
        j+=1

    print(message)
    client.chat_postMessage(channel=channel_id,text=message)
    return Response(),200


if __name__ == "__main__":
    app.run(debug=True, port=3000)
