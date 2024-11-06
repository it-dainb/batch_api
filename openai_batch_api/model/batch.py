from .file import File
from ..utils import get_prices

from openai import OpenAI
from datetime import datetime

from typing import Literal
from openai.types import Batch as OpenaiBatch

Status = Literal[
    None, "validating", "failed", "in_progress", "finalizing", "completed", "expired", "cancelling", "cancelled"
]

class Batch:
    def __init__(self, client: OpenAI, model_name: str, path: str, max_retry: int = 3, timeout: int = 60):
        self.id = None
        
        self.client = client
        self.model_name = model_name
        
        self.input_file = File(client, path)

        self.max_retry = max_retry
        self.timeout = timeout

        self.clean()

    def clean(self):
        self.id = None
        self.status: Status = None
        
        self.in_progress_at = None
        
        self.error_file = None
        self.output_file = None

        self.done = False

        self.usage = {
            "prompt": {
                "tokens": 0,
                "price": 0
            },
            "completion": {
                "tokens": 0,
                "price": 0
            }
        }

    def send(self) -> None:
        self.clean()
        
        batch: OpenaiBatch = self.client.batches.create(
            input_file_id=self.input_file.id,
            endpoint="/v1/chat/completions",
            completion_window="24h",
            metadata={
                "path": self.input_file.path
            }
        )

        self.id = batch.id
        self.status = batch.status

    def resend(self):
        if self.status == "in_progress":
            self.client.batches.cancel(self.id)
        
        self.send()
        self.max_retry -= 1

        if self.max_retry <= 0:
            self.done = True

    def need_resend(self):    
        if self.status in ["expired", "failed"] and self.max_retry > 0:
            return True

        if self.in_progress_at is not None and datetime.now().timestamp() - self.in_progress_at > self.timeout:
            return True

        return False

    def update_status(self, batch: OpenaiBatch) -> None:
        self.status = batch.status

        if self.status == "in_progress" and self.in_progress_at is None:
            self.in_progress_at = batch.in_progress_at

    def update_file(self, batch: OpenaiBatch) -> None:
        if self.status != "completed" or self.done:
            return

        if batch.request_counts.completed > 0:
            self.output_file = File(self.client, id = batch.output_file_id)
            self.update_usage(self.output_file)

        if batch.request_counts.failed > 0:
            self.error_file = File(self.client, id = batch.error_file_id)

        self.done = True

    def update_usage(self, file: File):
        self.usage["prompt"]["tokens"] += file.usage["prompt_tokens"]
        self.usage["completion"]["tokens"] += file.usage["completion_tokens"]

        prices = get_prices(
            self.model_name,
            {
                "prompt_tokens": self.usage["prompt"]["tokens"],
                "completion_tokens": self.usage["completion"]["tokens"],
            }
        )

        self.usage["prompt"]["price"] += prices["input"]
        self.usage["completion"]["price"] += prices["output"]

    def update(self) -> bool:
        batch: OpenaiBatch = self.client.batches.retrieve(self.id)

        self.update_status(batch)
        
        if self.need_resend():
            self.resend()
            
        self.update_file(batch)

        return self.done