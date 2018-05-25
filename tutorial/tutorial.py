from __future__ import print_function
from __future__ import absolute_import
from os.path import expanduser, join

from pymyra.api import client

# Create the API config object from a configuration object
config = {
    "account_id": "",
    "account_secret": ""
}

# Get from the Myra dashboard
INTENT_MODEL_ID = "941036122d9b421b89225976ff1ca3aa"

# Establish a global API connection
api = client.connect(config)
api.set_intent_model(INTENT_MODEL_ID)


class Actions(object):

    # Initialize a simple intent to action mapping
    def __init__(self):
        self.intent_map = {
            "cancel": self.cancel_handler,
            "create": self.create_handler,
            "help": self.help_handler,
            "unknown": self.unknown_handler
        }

    def handle(self, **kwargs):
        result = kwargs.get("result")
        intent = result.intent
        if intent.label not in self.intent_map:
            intent.label = "unknown"
            intent.score = 1
        return self.intent_map.get(intent.label)(**kwargs)

    # Handler functions for each intent
    def cancel_handler(self, **kwargs):
        api_result = kwargs.get("result")

        # See docs.myralabs.com for more information about entity and intent
        # API formats.

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

    def create_handler(self, **kwargs):
        api_result = kwargs.get("result")
        e = api_result.entities.entity_dict.get("builtin", {})
        message = "I can help create a meeting for you"
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

    def help_handler(self, **kwargs):
        api_result = kwargs.get("result")
        return "This is some help  %s %s" % (api_result.intent.label,
                                             api_result.intent.score)

    def unknown_handler(self, **kwargs):
        api_result = kwargs.get("result")
        return "I'm sorry I don't know how to handle this\ %s %s" % (
            api_result.intent.label, api_result.intent.score)


class CalendarBot(object):

    welcome_message = "Welcome to calendar bot! I can help you create and cancel meetings. Try 'set up a meeting with Jane' or 'cancel my last meeting' to get started."

    def __init__(self):
        self.actions = Actions()

    def process(self, user_input):
        result = api.get(user_input)
        message = self.actions.handle(result=result)
        print("calendar_bot>> ", message)

if __name__ == "__main__":
    bot = CalendarBot()
    c = client.CmdLineHandler(bot)
    c.begin(startMessage=bot.welcome_message,
            botName="calendar_bot")
