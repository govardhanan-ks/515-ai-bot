from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

class Utils:
    def __init__(self, url = os.environ["LLM_ENDPOINT"], model = os.environ["MODEL"]):
        self.url = url
        self.client = OpenAI(
            base_url=f"http://{self.url}/v1", 
            api_key="not-needed"  
        )
        self.model = model

    def generate_content(self, update):
        prompt = f""""
        You are an intelligent AI assistant tool.

        Your task is to do the following:
        1) You are given an input: {update}
        2) Remove User tag from the input
        3) With this input, you have to fix spelling and grammatical errors and generate a beautiful summary that should not exceed 200 words
        4) Give me the answer in neat bullet points instead of paragraphs

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




