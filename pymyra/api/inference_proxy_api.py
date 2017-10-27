import os
import logging

import inference_proxy_client
import messages
import client_base

log = logging.getLogger(__name__)

class InferenceProxyAPI(client_base.InferenceClientBase):

    def __init__(self, intent_model_id=None, entity_model_id=None,
                 params=None, inference_proxy_client=None,
                 service="cloudml"):
        self.intent_model_id = intent_model_id
        self.entity_model_id = entity_model_id
        self.params = params
        self.inference_proxy_client = inference_proxy_client
        if not self.inference_proxy_client:
            raise Exception("need to create a client")
        self.endpoint = "Classify"
        if service == "cloudml":
            self.endpoint = "CloudMLClassify"

    def set_intent_model(self, intent_model_id):
        self.intent_model_id = intent_model_id

    def set_params(self, params):
        self.params = params
        log.debug("setting params: %s", self.params)

    def set_entity_model(self, entity_model_id):
        self.entity_model_id = entity_model_id

    def get(self, text, intent_model_id=None, entity_model_id=None,
            url_params=None):
        _params = {"text":text}
        # Override parameters given in the constructor with those specified here.
        if not intent_model_id:
            intent_model_id = self.intent_model_id
        if intent_model_id:
            _params["intent_model_id"] = intent_model_id
        if not entity_model_id:
            entity_model_id = self.entity_model_id
        if entity_model_id:
            _params["entity_model_id"] = entity_model_id

        if url_params:
            _params.update(url_params)

        if self.params:
            _params.update(self.params)

        inference_result = self.inference_proxy_client.get(
            self.endpoint, _params)
        intent = None
        score = None
        entities = None
        if inference_result:
            if intent_model_id:
                (intent, score) = self._extract_intent(inference_result)
            entities = self._extract_entities(inference_result)

        # There are legacy reasons for the {"result":..}
        ir = messages.InferenceResult(intent, score, entities,
                                      {"result":inference_result})
        return ir



def test():
    host = os.getenv("MYRA_INFERENCE_PROXY_LB", "localhost")
    port = int(os.getenv("MYRA_INFERENCE_PROXY_LB_PORT", 7096))
    inf_proxy_client = inference_proxy_client.InferenceProxyClient(
        host=host, port=port)
    inf_proxy_api = InferenceProxyAPI(
        inference_proxy_client=inf_proxy_client)
    intent_model_id = os.getenv(
        "INTENT_MODEL_ID", "m-lica-02e90420e9b5f5f5eeb525e7d")
    text = os.getenv("TEXT", "i was charged for a cancelled ride")
    api_result = inf_proxy_api.get(
        text=text,
        intent_model_id=intent_model_id)
    print api_result


if __name__ == "__main__":
    test()

