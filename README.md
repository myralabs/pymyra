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

This will also install a sample configuration file into the following path `$HOME/.pymyra/settings.conf`.

## Overview

`pymyra` provides access to the Myra RESTful APIs. It currently supports `Python 2.7`.

To continue, create an account on http://api.myralabs.com, and from the `Explore API` tab, replace `account_id` and `account_secret` in the configuration file at `$HOME/.pymyra/settings.conf` with your credentials.

See the `tutorials` directory for a step by step tutorial and examples.

## Minimal Example

```
from os.path import expanduser, join
from pymyra.api import client

sentence = "whats a good coffee shop in the mission?"

# Create configuration
config = {
  "account_id": "",
  "account_secret": ""
}

# Connect API
api = client.connect(config)

# Set intent model
# Copy an ID from http://api.myralabs.com/v2/dashboard/#/intents
im = "xxxyyy"
api.set_intent_model(im)

# Set entity model
# Copy an ID from http://api.myralabs.com/v2/dashboard/#/entities
em = "aababb"
api.set_entity_model(em)

# Get results
result = api.get(sentence)

print("Intent: ", result.intent.label, result.intent.score)
print("Entities; ", result.entities.entity_dict)

```
