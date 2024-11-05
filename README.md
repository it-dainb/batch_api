# OpenaiBatchAPI: A Python Library that support OpenAI Batch API
[OpenAI Batch API](https://platform.openai.com/docs/guides/batch)

## Installation

You can install this package from PyPI using [pip](http://www.pip-installer.org):

```
$ pip install OpenaiBatchAPI
```

## Example

```python
#!/usr/bin/python
# -*- coding: utf-8 -*-
from batch_api import OpenaiBatchAPI

batch_client = OpenaiBatchAPI(api_key = "YOUR_KEY")

messages = [[
    {
        "role": "user",
        "content": "HI"
    }
]] * 23

batchs = batch_api.batchs_completion(messages)