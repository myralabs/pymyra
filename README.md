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

```
from pymyra.api import client

sentence = "whats a good coffee shop in the mission?"

# Create configuration
config = {
  "account_id": "", # replace with the correct IDs after creating an account
  "account_secret": ""
}

# Connect API
api = client.connect(config)

# Set intent model
im = "xxxyyy"
api.set_intent_model(im)

# Set entity model
em = "aababb"
api.set_entity_model(em)

# Get results
result = api.get(sentence)

print("Intent: ", result.intent.label, result.intent.score)
print("Entities; ", result.entities.entity_dict)

```
