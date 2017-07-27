import time
import json
import os
import sys
import random
import requests
import distutils
import logging

log = logging.getLogger(__name__)

MOCK_PREDICT_RESPONSE = {
   "customEntities": {
     "chunks": {
       "be": "it"
     },
     "key_phrases": [],
     "num_people": 2,
     "time": "Fri, 27 May 2016 02:57:58 GMT",
     "zip_code": None
   },
   "entities": {},
   "intent": {
     "intent": "mock:cold",
     "score": 0.7092279195785522
   },
   "sent": "will it be cold?"
 }


class InferenceProxyClient(object):

    def __init__(self, host, port, timeoutSeconds=180):
        self._mock_intent = distutils.util.strtobool(
            os.getenv("MYRA_MOCK_PREDICT_INTENT", "0"))
        if self._mock_intent:
            return
        self.host = host
        self.port = port
        self.session = requests.session()
        self.server = "http://%s:%s" % (host, port)
        self.timeoutSeconds = timeoutSeconds

    def get(self, endpoint, params):
        r = None
        if self._mock_intent:
            log.info("returning mock intent")
            return MOCK_PREDICT_RESPONSE
        log.info("server: %s", self.server)
        log.info("endpoint: %s", endpoint)
        log.info("url: %s", "%s/%s" % (self.server, endpoint))
        log.info("params: %s", params)

        try:
            r = self.session.get(
                url="%s/%s" % (self.server, endpoint),
                params=params,
                timeout=self.timeoutSeconds)

        except requests.exceptions.ReadTimeout:
            log.exception(
                "Timeout (%s): could not get reply from inference proxy",
                self.timeoutSeconds)
            raise
        except:
            log.exception("GOT exception")
            raise
        if not r or r.status_code in [404, 401, 403, 402, 500, 503]:
            #return flask_json.dumps({"status": "failure"})
            log.error("r: %s, returning status: failure", r)
            raise Exception("InferenceProxy.response: %s" % (r,))
        log.info("r.json(): %s", r.json())
        return r.json()

        
