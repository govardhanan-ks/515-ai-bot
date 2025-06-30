from openai import OpenAI
import os
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()

class Utils:
    def __init__(self, url = os.environ["LLM_ENDPOINT"], model = os.environ["MODEL"]):
        self.url = url
        self.client = OpenAI(
            base_url=f"http://{self.url}/v1", 
            api_key="not-needed"  
        )
        self.model = model
        self.gpt_model = os.environ["OPENAI_MODEL"]
        self.gpt_client = AzureOpenAI(
        api_key=os.environ["OPENAI_API_KEY"],
        api_version=os.environ["OPENAI_API_VERSION"],
        azure_endpoint=os.environ["OPENAI_AZURE_ENDPOINT"]
        )

        

    def generate_content(self, update):
        prompt = f""""
        You are an intelligent AI assistant tool.

        Your task is to do the following:
        1) You are given an input: {update}
        2) Remove User tag from the input
        3) With this input, you have to fix spelling and grammatical errors and generate a beautiful summary that should not exceed 200 words
        4) Give me the answer in neat bullet points instead of paragraphs, each point have to append in new line

        After generating this summary only return this summary as output and nothing else

        Return only the summary and nothing else.
        """

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "user", "content": prompt},
            ]
        )

        return(response.choices[0].message.content)

    def generate_gpt_content(self, update):
        prompt = f""""
        You are an intelligent AI assistant tool.

        Your task is to do the following:
        1) You are given an input: {update}
        2) Remove User tag from the input
        3) With this input, you have to fix spelling and grammatical errors and generate a beautiful summary that should not exceed 200 words
        4) Give me the answer in neat bullet points instead of paragraphs, each point have to append in new line

        After generating this summary only return this summary as output and nothing else

        Return only the summary and nothing else.
        """

        response = self.gpt_client.chat.completions.create(
                    model=self.gpt_model,  # your deployed model name
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                )

        return(response.choices[0].message.content.strip())






