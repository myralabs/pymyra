# pymyra

The Python SDK for the Myra Conversational AI REST API.

## Install

Using `pip`:
```bash
pip install pymyra
```

From source:
```bash
git clone https://github.com/myralabs/pymyra
cd pymyra
pip install .
```

## Overview

`pymyra` provides access to the Myra RESTful APIs. It currently supports `Python 2.7`.

To continue, create an account on http://api.myralabs.com, and copy your API credentials from the `Explore API` tab. You can then replace the empty `account_id` and `account_secret` fields in the example below with your own.

See the `tutorial` directory for a step by step tutorial and examples.

## Minimal Example

Put this in `test.py`:

```python
from pymyra.api import client

# Connect API
config = {
  "account_id": "",  # Replace with the correct IDs after creating an account.
  "account_secret": ""
}
api = client.connect(config)

# Set intent model
api.set_intent_model("xxxyyy")  # Fill in intent model id from dashboard.

# Set entity model
api.set_entity_model("aababb")  # Fill in entity model id from dashboard.

# Get results
result = api.get("whats a good coffee shop in the mission?")

print("Intent is '%s' with confidence %s" % (result.intent.label, result.intent.score))
print("Entities: %s" % result.entities.entity_dict)

```

and you'll get

```json
$ python test.py 
Sentence: Create a meeting with Alan Turing and Von Neumann next friday at 10am in Princeton
Inferred intent is 'create' with confidence 0.885836362839
Recognized entities are:
{
    "status": {
        "status_code": 200
    }, 
    "builtin": {
        "DATE": [
            {
                "date": "Fri, 28 Oct 2016 10:00:00 GMT", 
                "start": 9, 
                "end": 12, 
                "label": "next friday at 10am"
            }
        ], 
        "GPE": [
            {
                "start": 15, 
                "text": "Princeton", 
                "end": 16, 
                "label": "GPE"
            }
        ], 
        "TIME": [
            {
                "start": 12, 
                "text": "10am", 
                "end": 14, 
                "label": "TIME"
            }
        ], 
        "search_query": "Create meeting Alan Turing Von Neumann next friday 10 am Princeton", 
        "PERSON": [
            {
                "start": 4, 
                "text": "Alan Turing", 
                "end": 6, 
                "label": "PERSON"
            }, 
            {
                "start": 7, 
                "text": "Von Neumann", 
                "end": 9, 
                "label": "PERSON"
            }
        ]
    }, 
    "user_defined": {}
}
$
```
