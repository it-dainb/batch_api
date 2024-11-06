# OpenaiBatchAPI: A Python Library for OpenAI Batch API
[OpenAI Batch API Documentation](https://platform.openai.com/docs/guides/batch)

**Note:** *Currently supports only `gpt-4o` and `gpt-4o-mini` models.*

## Installation

Install the package from PyPI using [pip](http://www.pip-installer.org):

```bash
$ pip install OpenaiBatchAPI
```

## Usage Example

### Basic Example

```python
from openai_batch_api import OpenaiBatchAPI

# Initialize the Batch API client
batch_client = OpenaiBatchAPI(
    api_key="API_TOKEN",
    max_retry=3,
    timeout=5 * 60  # Timeout in seconds
)

messages = []

# Add messages with custom IDs (e.g., "calc_{i}")
for i in range(7):
    messages.append({
        "id": f"calc_{i}",
        "content": [
            {
                "role": "user",
                "content": f"Calculate: 1 + {i} = "
            }
        ]
    })

# Add messages with auto-generated IDs (index-based)
for i in range(7):
    messages.append({
        "role": "user",
        "content": f"Calculate: 1 + {i} = "
    })

# Execute batch completion
batchs = batch_client.batchs_completion(
    messages,
    max_completion_tokens=32,
    model="gpt-4o-mini",
    temperature=0,
    seed=42,
    batch_size=2
)

# Print batch outputs
for batch in batchs:
    print("BATCH ID:", batch.id)
    print("FILE ID:", batch.output_file.id)
    for content in batch.output_file.contents:
        print("Message ID:", content["id"])
        print("Response:", content["choices"][0]['message']['content'])
    print()
```

### Output Sample

The script will output results similar to this:

```plaintext
Preparing: 100%|███████████████████████| 4/4 [00:10<00:00,  2.74s/it]
Sending: 100%|█████████████████████████| 4/4 [00:02<00:00,  1.60it/s]
Processing: 100%|██████████████████████| 4/4 [00:12<00:00,  3.10s/it]

BATCH ID: batch_672b237c62f88190b0d69cbf789eb754
FILE ID: file-IlJUOenuE8p7okKB3TX2ANKW
Message ID: calc_0
Response: 1 + 0 = 1
Message ID: calc_1
Response: 1 + 1 = 2.

BATCH ID: batch_672b237ce4fc8190813e7b1239f0336d
FILE ID: file-hTFNk0uBC37plDaWtgYtD0Dr
Message ID: calc_2
Response: 1 + 2 = 3.
Message ID: calc_3
Response: 1 + 3 = 4.

BATCH ID: batch_672b237d937c8190a2ec942aa9401732
FILE ID: file-AbzBSJGl2pPU1B6KPmMuIDBB
Message ID: calc_4
Response: 1 + 4 = 5.
Message ID: calc_5
Response: 1 + 5 = 6.

BATCH ID: batch_672b237e076c8190807819fde4cdd093
FILE ID: file-jRAePmaheNSNAWYcawdmSgYF
Message ID: calc_6
Response: 1 + 6 = 7.
```

### Usage Statistics

The `print_usage_table` method outputs a table summarizing token usage and cost.

```python
batch_client.print_usage_table(digits=8)
```

This outputs:

```plaintext
+------------+--------+-------------+
| Category   | Tokens |       Price |
+------------+--------+-------------+
| Prompt     |    119 | $0.00000892 |
| Completion |     55 | $0.00001650 |
+------------+--------+-------------+
| Total      |    174 | $0.00002543 |
+------------+--------+-------------+
```