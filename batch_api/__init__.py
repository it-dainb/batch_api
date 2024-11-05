import uuid, orjsonl, os
from openai import OpenAI
import json
import time
import tempfile
from tqdm.auto import tqdm
from datetime import datetime

class OpenaiBatchAPI:
    def __init__(self, api_key: str = None, req_cooldown: float = 1.7, batch_cooldown: float = 0.052, batch_timeout: int = 5 * 60) -> None:
        """
        Initializes the OpenaiBatchAPI with the specified parameters.

        Args:
            api_key (str): The API key for authenticating with the OpenAI service. Defaults to None.
            req_cooldown (float): The cooldown period in seconds between requests. Defaults to 1.7.
            batch_cooldown (float): The cooldown period in seconds between batch operations. Defaults to 0.052.
            batch_timeout (int): The timeout in seconds for batch operations. Defaults to 300.

        Attributes:
            client (OpenAI): The OpenAI client initialized with the given API key.
            req_cooldown (float): The cooldown period in seconds between requests.
            batch_cooldown (float): The cooldown period in seconds between batch operations.
            batch_timeout (int): The timeout in seconds for batch operations.
        """

        self.client = OpenAI(api_key=api_key)
        self.req_cooldown = req_cooldown
        self.batch_cooldown = batch_cooldown
        self.batch_timeout = batch_timeout

    def prepare_reqs(self, messages: list, **kargs) -> list:
        """
        Prepares a list of request dictionaries for batch processing.

        Args:
            messages (list): A list of message objects or lists to be processed.
            **kargs: Additional keyword arguments to be included in the request body.

        Returns:
            list: A list of request dictionaries ready for processing.
        """
        
        reqs = []

        for i, message in enumerate(messages):
            if isinstance(message, list):
                message = {
                    "id": f"{self.identity}_{i}",
                    "content": message
                }
            else:
                message = {
                    "id": f"{self.identity}_{i}_{message['id']}",
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
    
    def prepare_batchs(self, reqs: list, batch_size: int = 20) -> dict:
        """
        Prepares a list of batches for processing.

        Args:
            reqs (list): A list of request dictionaries to be processed.
            batch_size (int): The maximum number of requests to include in a batch. Defaults to 20.

        Returns:
            dict: A dictionary containing the id of each batch file and its corresponding path.
        """

        files = {}

        for idx, i in enumerate(range(0, len(reqs), batch_size)):
            batch = reqs[i:i+batch_size]
            batch_path = os.path.join(self.batch_folder_path, f'{idx}.jsonl')
            orjsonl.save(batch_path, batch)
            
            batch_file = self.client.files.create(
                file=open(batch_path, "rb"),
                purpose="batch"
            )

            files[batch_file.id] = batch_path
        
        return files
            
    def setup(self, **kargs: dict) -> dict:
        """
        Sets up the batch API by generating a unique identity, setting the default model, creating a temporary directory for storing batch files, and updating the keyword arguments.

        Args:
            **kargs: A dictionary of keyword arguments.

        Returns:
            dict: The updated keyword arguments.
        """
        self.identity = uuid.uuid4().hex
        kargs['model'] = kargs.get('model', 'gpt-4o-mini')

        self.batch_folder = tempfile.TemporaryDirectory(prefix = f"{self.identity}_")
        self.batch_folder_path = self.batch_folder.name

        return kargs
    
    def clean_up(self) -> None:
        """
        Cleans up the batch API by deleting the temporary directory and resetting the identity.

        Args:
            None

        Returns:
            None
        """
        self.batch_folder.cleanup()
        self.batch_folder_path = None
        self.identity = None
    
    def send_batch(self, file_id: str, file_path: str) -> dict:
        """
        Sends a batch request for processing.

        Args:
            file_id (str): The ID of the file to be processed.
            file_path (str): The path to the file to be processed.

        Returns:
            dict: A dictionary containing the batch ID, file details, status, and output.
        """
        batch = self.client.batches.create(
            input_file_id=file_id,
            endpoint="/v1/chat/completions",
            completion_window="24h",
            metadata={
                "path": file_path
            }
        )

        return {
            "id": batch.id,
            "file": {
                "id": file_id,
                "path": file_path
            },
            "status": "validating",
            "output": None
        }
    
    def send_batchs(self, files: dict[str, str]) -> dict[str, dict]:
        """
        Sends a list of batch requests for processing.

        Args:
            files (dict[str, str]): A dictionary containing the file id as the key and the file path as the value.

        Returns:
            dict[str, dict]: A dictionary containing the file path as the key and the batch details as the value.
        """
        batchs = {}
        for file_id, file_path in tqdm(files.items(), total=len(files), desc="Sending"):
            batch = self.send_batch(file_id, file_path)
            time.sleep(self.batch_cooldown)

            batchs[file_path] = batch
        
        return batchs

    def get_output(self, file_id: str) -> list[dict[str, str | list[dict[str, str]]]]:
        """
        Retrieves the output of a batch request.

        Args:
            file_id (str): The file ID of the batch request.

        Returns:
            list[dict[str, str | list[dict[str, str]]]]: A list of dictionaries, each containing the custom ID and response.
        """
        data_str = self.client.files.content(file_id).text.strip()
        data = ",".join(data_str.split("\n"))
        data = f"[{data}]"
        datas = json.loads(data)

        datas = [
            {
                "custom_id": data["custom_id"],
                "response": data['response']['body']['choices']
            }
            for data in datas
        ]

        return datas
    
    def retrieve_batchs(self, batchs: dict[str, dict]) -> dict[str, dict]:
        """
        Retrieves the output of a list of batch requests.

        Args:
            batchs (dict[str, dict]): A dictionary containing the file path as the key and the batch details as the value.

        Returns:
            dict[str, dict]: A dictionary containing the file path as the key and the batch details as the value.
        """
        with tqdm(total=len(batchs), desc="Processing") as batch_pbar:
            while batch_pbar.n < len(batchs):
                for file_path, batch in batchs.items():
                    if batch["status"] == "completed":
                        continue

                    batch_obj = self.client.batches.retrieve(batch["id"])
                    time.sleep(self.req_cooldown)

                    status = batch_obj.status
                    batchs[file_path]["status"] = status
                    
                    try:
                        is_timeout = datetime.now().timestamp() - batch.in_progress_at > self.batch_timeout
                    except:
                        is_timeout = False

                    need_cooldown = False
                    if status == "completed":
                        batchs[file_path]["output"] = self.get_output(batch_obj.output_file_id)                        
                        batch_pbar.update(1)
                        need_cooldown = True
                        
                    elif status == "failed":
                        batch = self.send_batch(batch["file"]["id"], batch["file"]["path"])
                        batchs[file_path] = batch
                        need_cooldown = True

                    elif is_timeout and status == "in_progress":
                        self.client.batches.cancel(batch["id"])

                        batch = self.send_batch(batch["file"]["id"], batch["file"]["path"])
                        batchs[file_path] = batch
                        need_cooldown = True
                    
                    if need_cooldown:
                        time.sleep(self.req_cooldown)
        
        return batchs
        
    def batchs_completion(
        self,
        messages: list,
        **kargs: dict
    ) -> dict[str, dict[str, str | list[dict[str, str]]]]:
        """
        Processes a list of messages in batches and returns the output.

        Args:
            messages (list): A list of message objects or lists to be processed.
            **kargs: Additional keyword arguments to be included in the request body.

        Returns:
            dict[str, dict[str, str | list[dict[str, str]]]]: A dictionary containing the file path as the key and the output as the value.
        """
        kargs = self.setup(**kargs)

        reqs = self.prepare_reqs(messages, **kargs)
        files = self.prepare_batchs(reqs)
        batchs = self.send_batchs(files)
        batchs = self.retrieve_batchs(batchs)

        self.clean_up()

        return batchs
