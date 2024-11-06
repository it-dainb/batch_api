import json
from openai import OpenAI
from openai.types import FileObject

class File:
    def __init__(self, client: OpenAI, path: str = None, id: str = None):
        self.path = path
        self.client = client

        self.id = id
        self.contents = None

        self.usage = {
            "prompt_tokens": 0,
            "completion_tokens": 0
        }

        if self.path is not None:
            self.send()
        elif self.id is not None:
            self.get()
        
    def send(self) -> None:
        with open(self.path, "rb") as input_file:
            file: FileObject = self.client.files.create(
                file=input_file,
                purpose="batch"
            )

        self.id = file.id

    def get(self) -> None:
        file = self.client.files.content(self.id)
        
        data = file.text.strip()
        data = ",".join(data.split("\n"))
        data = f"[{data}]"

        datas = []
        for req in json.loads(data):
            custom_id = req["custom_id"].split("<custom_id>")[-1]
            body = req["response"]["body"]

            error = None
            choices = None
            usage = None
            if "error" in body:
                error = body["error"]
            else:
                choices = body["choices"]
                usage = body["usage"]

                self.usage['prompt_tokens'] += usage["prompt_tokens"]
                self.usage['completion_tokens'] += usage["completion_tokens"]

            datas.append({
                "id": custom_id,
                "choices": choices,
                "usage": usage,
                "error": error
            })

        
        self.contents = datas