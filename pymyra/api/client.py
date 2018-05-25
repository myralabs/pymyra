from __future__ import print_function
from __future__ import absolute_import
import os, sys
import requests
import json
import logging
from os.path import expanduser, join
import six.moves.configparser
import six.moves.urllib.request, six.moves.urllib.parse, six.moves.urllib.error
from six.moves import input
try:
    import http.client as http_client
except ImportError:
    # Python 2
    import six.moves.http_client as http_client

from . import messages
from . import client_base

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
                userInput = input("> ")
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
        self.config = six.moves.configparser.ConfigParser()
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



class InferenceClient(client_base.InferenceClientBase):
    def __init__(
            self,
            account_id, account_secret,
            intent_model_id=None, entity_model_id=None,
            myra_api_server=None, myra_api_version=None,
            params=None):
        log.debug("InferenceClient.__init__(%s)", locals())
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
             url_params=None):
        log.debug("_get(%s)", locals())
        url = "http://%s/api/%s/parse?text=%s" % (
            self.hostname, self.api_version, text)
        if intent_model_id:
            url += "&intent_model_id=%s" % (intent_model_id,)
        if entity_model_id:
            url += "&entity_model_id=%s" % (entity_model_id,)
        _params = {}
        if self.params:
            _params = self.params
        if url_params:
            _params.update(url_params)
        url += "&%s" % (six.moves.urllib.parse.urlencode(_params, doseq=True),)
        log.info("API CALL url: %s", url)
        r = self._session.get(url)
        if r.status_code != 200:
            print(r.__dict__)
            raise InferenceClientError(
                "Error: status_code %s" % (r.status_code,))
        log.info("API RETURN r.json: %s", r.json())
        return r.json()

    def _get_dict(self, text, intent_model_id, entity_model_id,
                  url_params=None):
        log.debug("_get_dict(%s)", locals())
        js = self._get(text, intent_model_id, entity_model_id,
                       url_params)
        log.debug(">>> js: %s", js)
        return js

    # Public API

    def set_intent_model(self, intent_model_id):
        self.intent_model_id = intent_model_id

    def set_params(self, params):
        self.params = params
        log.debug("setting params: %s", self.params)

    def set_entity_model(self, entity_model_id):
        self.entity_model_id = entity_model_id

    def get_intent(self, text, intent_model_id=None,
                   url_params=None):
        log.debug("InferenceClient.get_intent(%s)", locals())
        if not intent_model_id:
            intent_model_id = self.intent_model_id
        d = self._get_dict(text, intent_model_id, None,
                           url_params)
        (intent, score) = self._extract_intent(d.get("result"))
        return messages.IntentResult(intent, score)

    def get_entities(self, text, entity_model_id=None):
        if not entity_model_id:
            entity_model_id = self.entity_model_id
        d = self._get_dict(text, None, entity_model_id)
        e = self._extract_entities(d.get("result"))
        return messages.EntityResult(e)

    def get(self, text, intent_model_id=None, entity_model_id=None,
            url_params=None):
        log.debug("InferenceClient.get(%s)", locals())
        if not entity_model_id:
            entity_model_id = self.entity_model_id
        if not intent_model_id:
            intent_model_id = self.intent_model_id
        d = self._get_dict(text, intent_model_id, entity_model_id,
                           url_params)
        #log.debug("pymyra.client.get.d: %s", d)
        intent = None
        score = None
        entities = None
        if d:
            if intent_model_id:
                (intent, score) = self._extract_intent(d.get("result"))
            entities = self._extract_entities(d.get("result"))
        ir = messages.InferenceResult(intent, score, entities, d)
        #log.debug("returning InferenceResult: %s, ir.api_response: %s",
        #          ir, ir.api_response)
        return ir
