import os
from openai import AzureOpenAI

from deepeval import evaluate
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from deepeval.metrics import SummarizationMetric

class Evaluator:
    def __init__(self, url = os.environ["LLM_ENDPOINT"]):
        self.model = os.environ["OPENAI_MODEL"]
        self.client = AzureOpenAI(
        api_key=os.environ["OPENAI_API_KEY"],
        api_version=os.environ["OPENAI_API_VERSION"],
        azure_endpoint=os.environ["OPENAI_AZURE_ENDPOINT"]
        )

    def _generate_judgement(self, prompt):

        response = self.client.chat.completions.create(
                    model=self.model,  # your deployed model name
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                )

        return(response.choices[0].message.content.strip())

    def measure(self, test_case: LLMTestCase):
        prompt = f"""
        Evaluate how well the following summary captures the key points of the original input text.

        Input:
        {test_case.input}

        Summary:
        {test_case.actual_output}

        Respond with a score from 1 to 5 and a brief explanation.
        """

        judgement = self._generate_judgement(prompt)

        try:
            score_line = [line for line in judgement.splitlines() if any(d in line for d in "12345")][0]
            score = int("".join(filter(str.isdigit, score_line)))
        except Exception:
            score = 1  # default if parsing fails

        test_case.output = {
            "score": score,
            "explanation": judgement
        }

        print(test_case.output)
    def run_evaluation(self, input, model_summary):
        test_case = LLMTestCase(
            input = input,
            actual_output = model_summary
        )
        self.measure(test_case)
    def __call__(self, input, model_summary):
        self.run_evaluation(input, model_summary)
