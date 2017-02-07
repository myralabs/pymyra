from __future__ import print_function
import os, sys
import requests
import json
import logging
from os.path import expanduser, join
import ConfigParser
try:
    import http.client as http_client
except ImportError:
    # Python 2
    import httplib as http_client


#####################################
# Utilities for the Myra API tutorial
#####################################

class CmdLineHandler(object):
    """ Simple terminal REPL for bots
    """

    def __init__(self, bot):
        self.bot = bot

    # Begin your command line loop
    def begin(self, startMessage=None, botName=""):
        if startMessage:
            print("%s>> " % botName, startMessage)
        while True:
            try:
                userInput = raw_input("> ")
                if not userInput:
                    continue
                self.processMessage(userInput)
            except (KeyboardInterrupt, EOFError, SystemExit):
                break

    # Handle incoming messages and return the response
    def processMessage(self, userInput):
        return self.bot.process(userInput)

# Configuration management
class MyraConfig(object):
    def __init__(self, config_file = None):
        self.config_file = config_file
        if not self.config_file:
            self.config_file = "./settings.conf"
        self.config = ConfigParser.ConfigParser()
        self.config.read(self.config_file)

    def get(self, section):
        res = {}
        options = self.config.options(section)
        for option in options:
            try:
                res[option] = self.config.get(section, option)
                if res[option] == -1:
                    pass # Skip
            except:
                print("exception on %s!" % option)
                res[option] = None
        return res



# Logging and debug utilities
http_client.HTTPConnection.debuglevel = 0
#logging.basicConfig()
log = logging.getLogger(__name__)
#log.setLevel(logging.INFO)

def set_debug():
    http_client.HTTPConnection.debuglevel = 1
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True
    log.setLevel(logging.DEBUG)

# Package level functions

def get_config(config_file=None):
    return MyraConfig(config_file)

def connect(config, debug=False):

    if debug:
        set_debug()

    hostname = config.get("hostname", os.getenv(
        "MYRA_API_SERVER", "api.myralabs.com"))
    version = config.get("version", os.getenv(
        "MYRA_API_VERSION", "v2"))
    account_id = config.get("account_id")
    account_secret = config.get("account_secret")
    return InferenceClient(account_id = account_id,
                           account_secret = account_secret,
                           myra_api_server = hostname,
                           myra_api_version = version)

class InferenceClientError(Exception):
    pass

class IntentResult(object):
    def __init__(self, label, score):
        self.label = label
        self.score = score

    def __repr__(self):
        return "label: %s, score: %s" % (self.label, self.score)

class EntityResult(object):
    def __init__(self, entities):
        self.entity_dict = entities

    def __repr__(self):
        return "entity_dict: %s" % (self.entity_dict,)

class InferenceResult(object):

    def __init__(self, intent_label=None, intent_score=None, entities=None,
                 api_response=None):
        self.intent = IntentResult(intent_label, intent_score)
        self.entities = EntityResult(entities)
        self.api_response = api_response

    def __repr__(self):
        return "InferenceResult: {intent:%s} {entities:%s} {api_response: %s}" % (
            self.intent, self.entities, self.api_response)

class InferenceClient(object):
    def __init__(
            self,
            account_id, account_secret,
            intent_model_id=None, entity_model_id=None,
            myra_api_server=None, myra_api_version=None,
            params=None):

        self.account_id = account_id
        self.account_secret = account_secret
        self.intent_model_id = intent_model_id
        self.entity_model_id = entity_model_id
        self.params = params

        if myra_api_server:
            self.hostname = myra_api_server
        else:
            self.hostname = os.getenv(
                "MYRA_API_SERVER", "api.myralabs.com")

        if myra_api_version:
            self.api_version = myra_api_version
        else:
            self.api_version = os.getenv(
                "MYRA_INFERENCE_VERSION", "v2")

        self._session = requests.Session()
        self._session.headers.update(self._get_headers())

    def _get_headers(self):
        return {
            "X-ACCOUNT-ID": self.account_id,
            "X-ACCOUNT-SECRET": self.account_secret
        }

    def _get(self, text, intent_model_id, entity_model_id,
             outlier_cutoff=None):
        url = "http://%s/api/%s/parse?text=%s" % (
            self.hostname, self.api_version, text)
        if intent_model_id:
            url += "&intent_model_id=%s" % (intent_model_id,)
        if entity_model_id:
            url += "&entity_model_id=%s" % (entity_model_id,)
        if outlier_cutoff:
            url += "&outlier_cutoff=%s" % (outlier_cutoff,)
        log.debug("url: %s", url)
        r = self._session.get(url)
        if r.status_code != 200:
            print(r.__dict__)
            raise InferenceClientError(
                "Error: status_code %s" % (r.status_code,))
        log.debug("r.json: %s", r.json())
        return r.json()

    def _get_dict(self, text, intent_model_id, entity_model_id,
                  outlier_cutoff=None):
        js = self._get(text, intent_model_id, entity_model_id,
                       outlier_cutoff)
        log.debug(">>> js: %s", js)
        return js

    def _extract_intent(self, response_dict):
        """d: dict representing returned json
        """
        i = response_dict.get("result",{}).get("intents",{})
        status_code = i.get("status",{}).get("status_code")
        if not status_code or status_code != 200:
            return None
        d = i.get("user_defined",{})
        intent = d.get("intent")
        score = d.get("score")
        return (intent, score)

    def _extract_entities(self, response_dict):
        i = response_dict.get("result", {}).get("entities")
        status_code = i.get("status",{}).get("status_code")
        if status_code and status_code != 200:
            return None
        return i

    # Public API

    def set_intent_model(self, intent_model_id):
        self.intent_model_id = intent_model_id

    def set_params(self, params):
        self.params = params

    def set_entity_model(self, entity_model_id):
        self.entity_model_id = entity_model_id

    def get_intent(self, text, intent_model_id=None):
        if not intent_model_id:
            intent_model_id = self.intent_model_id
        d = self._get_dict(text, intent_model_id, None)
        (intent, score) = self._extract_intent(d)
        return IntentResult(intent, score)

    def get_entities(self, text, entity_model_id=None):
        if not entity_model_id:
            entity_model_id = self.entity_model_id
        d = self._get_dict(text, None, entity_model_id)
        e = self._extract_entities(d)
        return EntityResult(e)

    def get(self, text, intent_model_id=None, entity_model_id=None,
            outlier_cutoff=None):
        log.debug("InferenceClient.get(%s)", locals())
        if not entity_model_id:
            entity_model_id = self.entity_model_id
        if not intent_model_id:
            intent_model_id = self.intent_model_id
        if (not outlier_cutoff and self.params
            and self.params.get("outlier_cutoff")):
            outlier_cutoff = self.params.get("outlier_cutoff")
        d = self._get_dict(text, intent_model_id, entity_model_id,
                           outlier_cutoff)
        #log.debug("pymyra.client.get.d: %s", d)
        (intent, score) = self._extract_intent(d)

        entities = self._extract_entities(d)
        ir = InferenceResult(intent, score, entities, d)
        #log.debug("returning InferenceResult: %s, ir.api_response: %s",
        #          ir, ir.api_response)
        return ir
