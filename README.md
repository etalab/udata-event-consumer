# event-consumer

**⚠️ This repository is archived following the use of Webhooks instead of Kafka in udata.**

A udata plugin to consume kafka events

## Usage

Install the plugin package in you udata environment:

```bash
pip install udata-event-consumer
```

Then activate it in your `udata.cfg`:

```python
PLUGINS = ['event-consumer']
```

You are now ready to start your udata consumer:
```bash
udata event consume
```
