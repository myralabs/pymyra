class InferenceClientBase(object):
    @classmethod
    def _extract_intent(cls, response_dict):
        """d: dict representing returned json
        """
        i = response_dict.get("intents",{})
        status_code = i.get("status",{}).get("status_code")
        if not status_code or status_code != 200:
            return None
        d = i.get("user_defined",{})
        intent = d.get("intent")
        score = d.get("score")
        return (intent, score)

    @classmethod
    def _extract_entities(cls, response_dict):
        i = response_dict.get("entities")
        status_code = i.get("status",{}).get("status_code")
        if status_code and status_code != 200:
            return None
        return i

