# Mercury4Free Wrapper

A Python wrapper for the Mercury web API. (1000 tokens/second)

## Installation

```bash
pip install Mercury4Free
```

## Basic Usage

```python
from Mercury4Free.mercury import MercuryClient

client = MercuryClient()
response = client.send_message("What's the weather like?", reasoning_effort="medium")
print(response)
```

## Methods

### `send_message(prompt, reasoning_effort="medium")`
Returns the full response as a string.

### `stream_chat(messages, reasoning_effort="medium")`
Generates a stream of tuples: `(message_type, content)`.
- `message_type`: "text", "reasoning", "reasoning_start", "reasoning_end", "text_start", "text_end", "debug", "error", "done"
- `content`: The text/reasoning token, error message, or raw JSON object for signaling types.

## Reasoning Effort
The `reasoning_effort` must be one of:
- `instant`
- `low`
- `medium`
- `high`

If an invalid value is provided, a `ValueError` will be raised.

Feel free to fork, star, and use this wrapper in your projects! (Not affiliated with Inception Labs and could be taken down at any time)
