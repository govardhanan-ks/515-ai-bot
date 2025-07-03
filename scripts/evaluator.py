import os
from langchain_openai import AzureChatOpenAI
import json
from deepeval import evaluate
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from deepeval.metrics import GEval
from deepeval.metrics.g_eval import Rubric
from langchain.schema import HumanMessage, SystemMessage
from deepeval.models.base_model import DeepEvalBaseLLM
from deepeval.metrics.g_eval.g_eval import ReasonScore
from dotenv import load_dotenv

load_dotenv("../.env")

os.environ["DEEPEVAL_NO_PROGRESS_BAR"] = "1"

class PatchedGEval(GEval):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.evaluation_cost is None:
            self.evaluation_cost = 0.0

    async def _a_evaluate(self, *args, **kwargs):
        result = await super()._a_evaluate(*args, **kwargs)
        if self.evaluation_cost is None:
            self.evaluation_cost = 0.0
        return result

class Sidewing(DeepEvalBaseLLM):
    def __init__(
        self,
        model
    ):
        self.model = model
        self.evaluation_cost = 0
        self.client = AzureChatOpenAI(
            api_key=os.environ["OPENAI_API_KEY"],
            deployment_name=os.environ["OPENAI_MODEL"],
            azure_endpoint=os.environ["OPENAI_AZURE_ENDPOINT"],
            api_version=os.environ["OPENAI_API_VERSION"],
            model= os.environ["OPENAI_MODEL"],
            temperature=0.3
        )

    def load_model(self):
        return self.model

    async def a_generate_raw_response(self, prompt: str, **kwargs):
        # Used by DeepEval internally
        response = self.generate(prompt, **kwargs)
        raw_response = response.content.strip()

    # Validate the output is a JSON string (optional, good for debugging)
        try:
            parsed = json.loads(raw_response)
            print(json.dumps(parsed, indent=4))
            assert "score" in parsed and "reason" in parsed
            
        except Exception as e:
            raise ValueError(f"Expected JSON with 'score' and 'reason', got: {raw_response}") from e

        return raw_response, 0.0

    async def a_generate(self, prompt: str, **kwargs):
        return self.generate(prompt, **kwargs)
    
    def get_model_name(self):
        return self.model
    
    def generate(self, prompt: str, **kwargs) -> str:
        messages = [
            SystemMessage(content="You are a helpful assistant."),
            HumanMessage(content=prompt)
        ]
        response = self.client.invoke(messages)

        return response

class Evaluator:
    def __init__(self, url = os.environ["LLM_ENDPOINT"]):
        self.model = os.environ["OPENAI_MODEL"]
        self.sidewing = Sidewing(self.model)
        relevancy_metric = PatchedGEval(
            name="Relevant",
            criteria="The summary retains important points and details from the source text",
            evaluation_steps=[
                "Check whether the facts in 'actual output' contradicts any facts in 'input'",
                "You should also heavily penalize omission of detail",
                "Vague language, or contradicting OPINIONS, are OK"
            ],
            rubric=[
                Rubric(score_range=(0,2), expected_outcome="Factually incorrect."),
                Rubric(score_range=(3,6), expected_outcome="Mostly correct."),
                Rubric(score_range=(7,9), expected_outcome="Correct but missing minor details."),
                Rubric(score_range=(10,10), expected_outcome="100% correct."),
            ],
            model = self.sidewing,
            async_mode = False,
            evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
        )

        conciseness_metric = PatchedGEval(
            name="Concise",
            criteria="The summary is information-dense, does not repeat the same point multiple times, and is not necessarily verbose",
            evaluation_steps=[
                "Check whether the facts in 'actual output' is smaller than the 'input'",
                "You should also heavily penalize repetition of info",
                "Capturing the important details of the 'input' in the 'actual output' is accepted"
            ],
            rubric=[
                Rubric(score_range=(0,2), expected_outcome="Almost the same size as the input itself"),
                Rubric(score_range=(3,6), expected_outcome="Repeats most points"),
                Rubric(score_range=(7,9), expected_outcome="Fine, but has some unnecessary detail"),
                Rubric(score_range=(10,10), expected_outcome="Perfectly information dense and does not repeat any points"),
            ],
            model = self.sidewing,
            async_mode = False,
            evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
        )

        coherency_metric = PatchedGEval(
            name="Coherent",
            criteria="The summary is well structured and easy to follow, not just a jumble of condensed facts",
            evaluation_steps=[
                "Check whether the facts in 'actual output' is properly structured",
                "You should also heavily penalize big paragraphs of data in 'actual output'",
            ],
            model = self.sidewing,
            async_mode = False,
            evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
        )

        faithfulness_metric = PatchedGEval(
            name="Faithful",
            criteria="The summary does not hallucinate information that is not supported by the source text",
            evaluation_steps=[
                "Check whether the facts in 'actual output' are not part of the in 'input'",
                "You should also heavily penalize adding unnecessary hallucinated information",
            ],
            model = self.sidewing,
            async_mode = False,
            evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
        )

        self.evaluation_metrics = [relevancy_metric, conciseness_metric, coherency_metric, faithfulness_metric]

        for metric in self.evaluation_metrics:
            metric.evaluation_cost = 0.0

    def measure(self, test_case: LLMTestCase):
        results = evaluate(test_cases=[test_case], metrics=self.evaluation_metrics)
        for result in results:
            for metric_result in result.metric_results:
                if hasattr(metric_result, 'evaluation_cost'):
                    delattr(metric_result, 'evaluation_cost')  # Optional cleanup
            print(result.to_dict()) 
    def run_evaluation(self, input, model_summary):
        test_case = LLMTestCase(
            input = input,
            actual_output = model_summary
        )
        self.measure(test_case)
    def __call__(self, input, model_summary):
        self.run_evaluation(input, model_summary)

if __name__ == "__main__":
    inp = "Dummy Summary"
    model_summary = "Generate a dummy summary for me"

    eval = Evaluator()
    eval(inp, model_summary)
