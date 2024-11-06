# OpenaiBatchAPI: A Python Library that support OpenAI Batch API
[OpenAI Batch API](https://platform.openai.com/docs/guides/batch)

## Installation

You can install this package from PyPI using [pip](http://www.pip-installer.org):

```
$ pip install openai_batch_api
```

## Example

```python
from openai_batch_api import OpenaiBatchAPI

batch_client = OpenaiBatchAPI(api_key = "YOUR_KEY")

messages = []

# For custom ID 
for i in range(23):
    messages.append(
        {
            "id": f"calc_{i}",
            "content": [
                {
                    "role": "user",
                    "content": f"Calculate:  1 + {i} = "
                }
            ]
        }
    )

# For auto ID (ID will be the index of the message in the list)
for i in range(23):
    messages.append(
        {
            "role": "user",
            "content": f"Calculate:  1 + {i} = "
        }
    )


batchs = batch_client.batchs_completion(
    messages, 
    max_completion_tokens=32,
    model="gpt-4o-mini",
    temperature=0,
    seed=42
)