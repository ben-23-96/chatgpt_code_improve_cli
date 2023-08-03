import asyncio
import aiohttp
import json
from os import path
from markdown_it import MarkdownIt

class GptRequest:
    def __init__(self, gpt_4: bool = False, temp: float = 0.4):
        """
    Parameters:
    - gpt_4 (bool): Whether to use GPT-4 API or not. Default is False.
    - temp (float): The temperature parameter for generating responses. Default is 0.4.
    """
        self.gpt_4 = gpt_4
        self.temp = temp
        self.prompts = []
        self.GPT_API_KEY = ""
        self.edited_functions = []

    def get_api_key(self):
        """
        Retrieve the OpenAI API key from a configuration file in the user's home directory.
    
        Raises:
            Exception: If the configuration file is not found.
        """
    
        # Define the directory and file path for the configuration file
        config_dir = path.expanduser('~/.chatgpt_cli/')
        config_file = path.join(config_dir, 'config.txt')
    
        try:
            # Attempt to open and read the API key from the configuration file
            with open(config_file, 'r') as f:
                # set the api_key to the one found in the file
                self.GPT_API_KEY = f.read().strip()
        except FileNotFoundError:
            # If the file is not found, raise an exception instructing the user to set the API key
            raise Exception('API key not found. Please set your API key using set-api-key command.')

    def create_prompts(self, functions: list, refactor: bool = False, comments: bool = False, docstrings: bool = False, error_handling: bool = False):
        """
    Creates the prompts to be sent to GPT API.
    
    Args:
        functions (list): A list of Python functions.
        refactor (bool, optional): Whether to refactor the code for better readability and performance. Defaults to False.
        comments (bool, optional): Whether to add comments to explain the function code. Defaults to False.
        docstrings (bool, optional): Whether to add a docstring to the function. Defaults to False.
        error_handling (bool, optional): Whether to improve the error handling. Defaults to False.
    """
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
        """
    Makes GPT requests asynchronously using asyncio.
    
    Returns:
        edited_functions (list): A list of edited functions.
    """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.async_GPT_requests())
        return self.edited_functions

    async def async_GPT_requests(self):
        """
    Sends asynchronous requests to GPT and extracts code from the responses.
    """
        tasks = []
        sem = asyncio.Semaphore(5)  # Adjust to preferred concurrent request limit

        async with aiohttp.ClientSession() as session:
            # make requests to api asynchronously
            for prompt in self.prompts:
                tasks.append(self.send_request(session, prompt))
            responses = await asyncio.gather(*tasks)

        for response in responses:
            # get the code as a string from the api response
            response_object = json.loads(response)
            message_content = response_object["choices"][0]["message"]["content"]
            self.extract_code_from_response(message_content)

    async def send_request(self, session, prompt):
        """
    Sends a request to the OpenAI API to generate a completion based on the given prompt.

    Args:
        session: An async session object for making HTTP requests.
        prompt: The prompt containing the function to edit and how it is to be edited.

    Returns:
        The generated completion as a string.
    """
        # Determine the model to use based on the value of self.gpt_4
        if self.gpt_4:
            model = 'gpt-4'
        else:
            model = 'gpt-3.5-turbo-16k'
    
        # Create the prompt message with system and user roles
        prompt_message = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    
        # URL for the API endpoint
        url = "https://api.openai.com/v1/chat/completions"
    
        # headers for the HTTP request
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.GPT_API_KEY}'
        }
    
        # data payload for the HTTP request
        data = {
            'model': model,
            'messages': prompt_message,
            'temperature': self.temp
        }
    
        # Send the HTTP request to the API endpoint and retrieve the response
        async with session.post(url, headers=headers, data=json.dumps(data)) as resp:
            return await resp.text()

    def extract_code_from_response(self, response: str):
        """
    Extracts Python code blocks from a Markdown response.

    Args:
        response (str): The Markdown response.

    Returns:
        str: The extracted Python code block.
    """
        md = MarkdownIt()  # Create an instance of the MarkdownIt class

        tokens = md.parse(response)  # Parse the Markdown response into tokens

        # Extract code blocks that are written in Python
        code_blocks = [t.content for t in tokens if t.type == 'fence' and t.info == 'python']

        self.edited_functions.append(code_blocks[0])  # Append the first code block to the edited_functions list
