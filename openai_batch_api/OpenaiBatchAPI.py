from .model import Batch
from openai import OpenAI

from tqdm.auto import tqdm
from prettytable import PrettyTable
import uuid, orjsonl, os, time, math
from tempfile import TemporaryDirectory

class OpenaiBatchAPI:
    def __init__(
        self, 
        api_key: str = None, 
        req_cooldown: float = 1.7, 
        batch_cooldown: float = 0.052, 
        timeout: int = 5 * 60,
        max_retry: int = 3
    ) -> None:

        self.client: OpenAI = OpenAI(api_key=api_key)
        self.req_cooldown = req_cooldown
        self.batch_cooldown = batch_cooldown

        self.timeout = timeout
        self.max_retry = max_retry

    def prepare_reqs(self, messages: list, **kargs) -> list:
        reqs = []

        for i, message in enumerate(messages):
            if isinstance(message, list):
                message = {
                    "id": f"{self.identity}_{i}",
                    "content": message
                }
            else:
                message = {
                    "id": f"{self.identity}_{i}<custom_id>{message['id']}",
                    "content": message["content"]
                }

            req = {
                "custom_id": message["id"],
                "method": "POST",
                "url": "/v1/chat/completions",
                "body": {
                    "messages": message["content"],
                    **kargs
                }
            }

            reqs.append(req)
        
        return reqs
    
    def setup(self, **kargs: dict) -> dict:
        self.identity = uuid.uuid4().hex

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

        kargs['model'] = kargs.get('model', 'gpt-4o-mini')

        if "gpt-4o" not in kargs['model']:
            raise ValueError("Model must be gpt-4o or gpt-4o-mini")

        return kargs
        
    def prepare_batchs(self, reqs: list, model_name: str, batch_size: int = 20) -> list[Batch]:

        batchs = []
        total_batches = math.ceil(len(reqs) / batch_size)

        with TemporaryDirectory(prefix = f"{self.identity}_") as batch_folder_path:
            for idx, i in tqdm(enumerate(range(0, len(reqs), batch_size)), total=total_batches, desc="Preparing"):
                batch = reqs[i:i+batch_size]
                batch_path = os.path.join(batch_folder_path, f'{idx}.jsonl')
                orjsonl.save(batch_path, batch)

                batchs.append(Batch(
                    client=self.client,
                    model_name = model_name,
                    path=batch_path,
                    max_retry=self.max_retry,
                    timeout=self.timeout
                ))
                time.sleep(self.batch_cooldown)

        return batchs
    
    def send_batchs(self, batchs: list[Batch]) -> None:
        for batch in tqdm(batchs, desc="Sending"):
            batch.send()
            time.sleep(self.batch_cooldown)

    def update_usage(self, batch: Batch) -> None:
        batch_usage = batch.usage
        
        self.usage["prompt"]["tokens"] += batch.usage["prompt"]["tokens"]
        self.usage["completion"]["tokens"] += batch.usage["completion"]["tokens"]

        self.usage["prompt"]["price"] += batch_usage["prompt"]["price"]
        self.usage["completion"]["price"] += batch_usage["completion"]["price"]
    
    def processing_batchs(self, batchs: list[Batch]) -> None:
        with tqdm(total=len(batchs), desc="Processing") as batch_pbar:
            while batch_pbar.n < len(batchs):
                for batch in batchs:
                    if batch.done:
                        continue
                    
                    if batch.update():
                        batch_pbar.update(1)
                        self.update_usage(batch)

                    time.sleep(self.req_cooldown)

    def batchs_completion(
        self,
        messages: list,
        batch_size:int = 20,
        **kargs: dict
    ) -> list[Batch]:

        kargs = self.setup(**kargs)

        reqs = self.prepare_reqs(messages, **kargs)
        
        batchs = self.prepare_batchs(reqs, kargs["model"], batch_size)
        
        self.send_batchs(batchs)
        self.processing_batchs(batchs)

        return batchs

    def print_usage_table(self, digits=8):
        table = PrettyTable()
        table.field_names = ["Category", "Tokens", "Price"]
        
        table.align["Category"] = "l"
        table.align["Tokens"] = "r"
        table.align["Price"] = "r"

        total_tokens = 0
        total_price = 0

        for idx, (category, data) in enumerate(self.usage.items()):
            tokens = data["tokens"]
            price = data["price"]
            table.add_row(
                [category.capitalize(), tokens, f"${price:.{digits}f}"],
                divider=idx == len(self.usage) - 1
            )
            total_tokens += tokens
            total_price += price

        table.add_row(["Total", total_tokens, f"${total_price:.{digits}f}"])

        print(table)