
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

