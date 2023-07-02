import asyncio
import aiohttp
import json
from os import environ
from markdown_it import MarkdownIt

class GptRequest:
    def __init__(self, gpt_4: bool = False, temp: float = 0.4):
        self.gpt_4 = gpt_4
        self.temp = temp
        self.prompts = []
        self.GPT_API_KEY = environ.get("GPT_API_KEY")
        self.edited_functions = []

    def create_prompts(self, functions: list, refactor: bool = False, comments: bool = False, docstrings: bool = False, error_handling: bool = False):

        for function in functions:
    
            prompt = f"Here is a Python function and I want you to do the following to it:"
            
            if refactor:
                prompt += "\n • Refactor the code for better readability and performance."
            if comments:
                prompt += "\n • Add comments to explain the function code."
            if docstrings:
                prompt += "\n • Add a docstring to the function."
            if error_handling:
                prompt += "\n • Improve the error handling."
        
            prompt += f"\n\nPlease make sure to return only the newly edited function code in your response, without any additional text or explanation outside of the function code. The code should be enclosed in triple backticks like this:\n\n\\```python\n<your code here>\n\\```\nThe original function is:\n\n{function}"

            self.prompts.append(prompt)

    def make_GPT_requests(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.async_GPT_requests())
        return self.edited_functions
                
    async def async_GPT_requests(self):
        tasks = []
        sem = asyncio.Semaphore(5)  # Adjust to preferred concurrent request limit
    
        async with aiohttp.ClientSession() as session:
            for prompt in self.prompts:
                tasks.append(self.send_request(session, prompt))
            responses = await asyncio.gather(*tasks)
    
        for response in responses:
            response_object = json.loads(response)
            message_content = response_object["choices"][0]["message"]["content"]
            self.extract_code_from_response(message_content)
    
    async def send_request(self, session, prompt):
        if self.gpt_4:
            model = 'gpt-4'
        else:
            model = 'gpt-3.5-turbo-16k'
        prompt_message = [{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": prompt}]
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.GPT_API_KEY}'
        }
        data = {
            'model': model,
            'messages': prompt_message,
            'temperature': self.temp
        }
    
        async with session.post(url, headers=headers, data=json.dumps(data)) as resp:
            return await resp.text()
     
    def extract_code_from_response(self, response: str):
        md = MarkdownIt()
    
        tokens = md.parse(response)
    
        code_blocks = [t.content for t in tokens if t.type == 'fence' and t.info == 'python']

        self.edited_functions.append(code_blocks[0])