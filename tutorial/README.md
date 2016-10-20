# Myra tutorial -- Zero to bot in 10 minutes

## Overview

Myra’s APIs are the best way to build natural language understanding into your applications. They provide tools to identify user intent, and extract key data like names, cities, numbers, and custom-defined values.

We'll build a simple and state-of-the-art conversational bot that will do this:

```

> cancel my meeting with Jane tomorrow at 9pm
>>  Sure, I'll cancel the meeting for you with Jane at Mon, 17 Oct 2016 21:00:00 GMT.

> create a meeting with Jane and Joe next saturday at 17:00 hours
>>  I can help create a meeting for you with Jane and Joe at Sat, 22 Oct 2016 17:00:00 GMT.

```

## Step 1: Install the SDK and the tutorial files

`pymyra` provides access to the Myra RESTful APIs. It currently supports `python 2.7`. To install pymyra as well as download the data for the tutorial, run:

```
git clone https://github.com/myralabs/pymyra
cd pymyra
pip install .
```


## Step 2: Configure the SDK with your API credentials

- Register at http://api.myralabs.com/register
- When your account is opened, you'll receive an email with a link to the dashboard.
- Log in to the dashboard and note the `account_id` and `account_secret`. Add those values into the appropriate places when initializing the client. See the main README for `pymyra` for a simple example.


## Step 3: Interact with CalendarBot

In the `pymyra` source directory, go to `tutorial/` and run `python tutorial.py`.

Meet CalendarBot! Ask it a question about creating or cancelling meetings.

```

python tutorial.py

**calendar_bot>>  Welcome to calendar bot! I can help you create and cancel meetings. Try 'set up a meeting with Jane' or 'cancel my last meeting' to get started.**

> cancel Jane's meeting with me tomorrow at 9pm
calendar_bot>>  Sure, I'll cancel the meeting for you with Jane at Mon, 17 Oct 2016 21:00:00 GMT.

> create a meeting with Jane and Joe next saturday at 17:00 hours
calendar_bot>>  I can help create a meeting for you with Jane and Joe at Sat, 22 Oct 2016 17:00:00 GMT.

```

## Step 4: Learn how CalendarBot is built

CalendarBot understands questions about creating and cancelling calendar entries. Later, we'll add the ability to modify entries. (CalendarBot doesn't actually connect to a calendaring service, sorry!)

CalendarBot is connected to pre-trained models that determine the user's intent -- the 'thing' they are trying to accomplish -- and the user's entities -- information in the sentence you need to carry out the user's task. We've included the (sample) training data for these models in `tutorial/data/botv1`.

### The model

The files are divided into two portions called `train` and `test`. The Myra model will learn based on the sentences in `train` and use the sentences in `test` to evaluate the model's performance on new, unseen data.

*botv1_train.tsv:*
```
utterance	intent
meeting with Kevin and John next tuesday 5pm	create
hang next week	create
let's meet up next week sometime	create
meeting with the team 10/24 in Guitar Hero	create
let's get everybody together	create
...
```
*botv1_test.tsv:*
```
utterance	intent
meet with steve and andy on weds	create
get together next friday	create
dinner on oct 25	create
set a meeting with everyone at 5pm	create
...
```
The train file has 12 utterances for `create` and 11 for `cancel`. We recommend at least 7-10 utterances for training files, and 3-5 for test files. Curious how it works? In Step 5, we'll walk through adding a new intent to the model and to the bot.

### The bot
`pymyra.api` contains the `client` module which we use to connect to the Myra API.

```python
from pymyra.api import client

# Create the API config object from a configuration object
config = {
  "account_id": "", # replace with the correct IDs after creating an account
  "account_secret": ""
}

api = client.connect(config)

# This is the demo model that ships with new Myra accounts.
INTENT_MODEL_ID = "941036122d9b421b89225976ff1ca3aa"

# Establish a global API connection
api = client.connect(config)
api.set_intent_model(INTENT_MODEL_ID)
```
In the `__main__` block, we initialize bootstrap code to set up a command line interaction.

```python
if __name__ == "__main__":
    # Initialize the calendar bot class
    bot = CalendarBot()

    # Start a simple command line handler to process incoming messages
    # and return a response
    c = client.CmdLineHandler(bot)
    c.begin(startMessage=bot.welcome_message,
      botName="calendar_bot")
```
Let's step through how we implement `CalendarBot`.

The `process()` function takes in a user input, invokes the Myra API on it via `api.get(user_input)`, and then passes this to the action handler function. The result from this call is then printed out on the terminal.

```python
result = api.get(user_input)
message = self.actions.handle(result=result)
print("calendar_bot>> ", message)
```
The last part of this file is the `Actions` class. This contains a simple mapping of intents to action handlers. For instance, if the bot detects that the user is asking to create a meeting, it'll invoke the `create_handler()` function.

Next, we define each handler function. Here's the code for the `cancel_handler`:

```python
 def cancel_handler(self, **kwargs):
        api_result = kwargs.get("result")
        e = api_result.entities.entity_dict.get("builtin", {})
        message = "Sure, I'll cancel the meeting for you"
        if "PERSON" in e:
            person = [i.get("text") for i in e.get("PERSON")]
            person_text = ""
            if len(person) > 1:
                person_text = " and ".join(person)
            else:
                person_text = person[0]
            message += " with %s" % person_text

        if "DATE" in e:
            tm = [i.get("date") for i in e.get("DATE")]
            tm_text = ""
            if len(tm) >= 1:
                tm_text = tm[0]
            message += " at %s." % (tm_text)
        return message
```

The function gets the result of the Myra API, and fetches the detected entities into `e`. If it finds a mention of a person and a time, it will include those in the response message.

## Step 5: Train and extend CalendarBot to handle something new
Now, let's add the ability to modify meetings to the Myra API and then to the bot.

### Train the model to recognize the modify intent
In `tutorial/data/botv2`, we've included new utterances for the intent `modify`. Check them out now:

*botv2_train.tsv:*
```
...
change the time of the meeting with deepak	modify
do the meeting with Jane at 1pm instead	modify
switch the 1:1 to 9am on tuesday	modify
```
The model was pretrained for the `create` and `cancel` intents; now, we'll upload and train the model ourselves to add the `modify` intent. To do so, go to the "Intent Models" section of the Myra dashboard.

* Create a new model named `tutorial_botv2` and click the green plus icon.
* Upload `botv2_train.tsv` into the Train section and `botv2_test.tsv` into the Test section, and hit Save and then Train.
* The model will take a few minutes to train. Once the status says 'Ready', copy the intent model's ID over to `INTENT_MODEL_ID` in `tutorial.py`.

### Add modify to the bot
Create a new entry in `self.intent_map` in the `Actions` class:
```python
{
..,
"modify": self.modify_handler
}
```
Next, define a new function called `modify_handler` in the `Actions` class.
```python
 def modify_handler(self, **kwargs):
        api_result = kwargs.get("result")
        e = api_result.entities.entity_dict.get("builtin", {})
        message = "Sure, I can modify the meeting for you"
        if "PERSON" in e:
            person = [i.get("text") for i in e.get("PERSON")]
            person_text = ""
            if len(person) > 1:
                person_text = " and ".join(person)
            else:
                person_text = person[0]
            message += " with %s" % person_text

        if "DATE" in e:
            tm = [i.get("date") for i in e.get("DATE")]
            tm_text = ""
            if len(tm) >= 1:
                tm_text = tm[0]
            message += " at %s." % (tm_text)
        return message

```

Run `tutorial.py` again, and ask the bot: "change my meeting with Scott to Tuesday", or whatever you want! Now, you have a bot that you've taught to understand complex input related to creating, modifying, and cancelling meetings.

## Next steps

You've made it! You now have a simple bot capable of understanding complex sentences related to creating, modifying, and canceling calendar entries. Next, try creating a new intent model for your own topics by adding sample utterances into the calendar data files.
