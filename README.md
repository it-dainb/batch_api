# OpenaiBatchAPI: A Python Library that support OpenAI Batch API
[OpenAI Batch API](https://platform.openai.com/docs/guides/batch)

NOTES: CURENTLY SUPPORT ONLY gpt4o AND gpt4o-mini

## Installation

You can install this package from PyPI using [pip](http://www.pip-installer.org):

```
$ pip install OpenaiBatchAPI
```

## Example

```python
from openai_batch_api import OpenaiBatchAPI

batch_client = OpenaiBatchAPI(
    api_key = "API_TOKEN",
    max_retry = 3,
    timeout = 5 * 60 # seconds
)

messages = []

# For custom ID (ID is set to "calc_{i}" for each message)
for i in range(7):
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
for i in range(7):
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
    seed=42,
    batch_size=2
)

for batch in batchs:
    print("BATCH :", batch.id)
    print("FILE  :", batch.output_file.id)
    for content in batch.output_file.contents:
        print("ID", content["id"])
        print(" => ", content["choices"][0]['message']['content'])
    print()
```

```bash
Preparing: 100%|███████████████████████| 4/4 [00:10<00:00,  2.74s/it]
Sending: 100%|█████████████████████████| 4/4 [00:02<00:00,  1.60it/s]
Processing: 100%|██████████████████████| 4/4 [00:12<00:00,  3.10s/it]
BATCH : batch_672b237c62f88190b0d69cbf789eb754
FILE  : file-IlJUOenuE8p7okKB3TX2ANKW
ID calc_0
 =>  1 + 0 = 1
ID calc_1
 =>  1 + 1 = 2.

BATCH : batch_672b237ce4fc8190813e7b1239f0336d
FILE  : file-hTFNk0uBC37plDaWtgYtD0Dr
ID calc_2
 =>  1 + 2 = 3.
ID calc_3
 =>  1 + 3 = 4.

BATCH : batch_672b237d937c8190a2ec942aa9401732
FILE  : file-AbzBSJGl2pPU1B6KPmMuIDBB
ID calc_4
 =>  1 + 4 = 5.
ID calc_5
 =>  1 + 5 = 6.

BATCH : batch_672b237e076c8190807819fde4cdd093
FILE  : file-jRAePmaheNSNAWYcawdmSgYF
ID calc_6
 =>  1 + 6 = 7.
 ```

```python
batch_client.print_usage_table(digits=8)
```

```bash
+------------+--------+-------------+
| Category   | Tokens |       Price |
+------------+--------+-------------+
| Prompt     |    119 | $0.00000892 |
| Completion |     55 | $0.00001650 |
+------------+--------+-------------+
| Total      |    174 | $0.00002543 |
+------------+--------+-------------+
```