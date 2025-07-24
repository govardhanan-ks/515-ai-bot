import os
from openai import AzureOpenAI
import json
from dotenv import load_dotenv
import pandas as pd


load_dotenv("../.env")

class Evaluator:
    def __init__(self, url = os.environ["LLM_ENDPOINT"]):
        self.model = os.environ["OPENAI_MODEL"]
        self.sidewing = AzureOpenAI(
        api_key=os.environ["OPENAI_API_KEY"],
        api_version=os.environ["OPENAI_API_VERSION"],
        azure_endpoint=os.environ["OPENAI_AZURE_ENDPOINT"]
        )

    def build_metric_prompt(self, metric_name, input_text, generated_output, criteria, steps, rubric):
        prompt = f"""You are a strict evaluator of summaries using the metric: {metric_name}.

                ## Input Document:
                {input_text}

                ## LLM Generated Summary:
                {generated_output}

                ## Evaluation Criteria:
                {criteria}

                ## Evaluation Steps:
                {chr(10).join(f"- {step}" for step in steps)}

                ## Rubric:
                {chr(10).join(f"- {r['score_range']}: {r['expected_outcome']}" for r in rubric)}

                Evaluate the summary and Respond ONLY in **valid JSON**, no extra commentary, no markdown formatting. Format:

                {{
                "metric": {metric_name}
                "score": integer between 0 and 10,
                "reason": explanation for the score
                }}"""

        return prompt

    def measure_relevancy_score(self, inp, llm_out):
        prompt_text = self.build_metric_prompt(
            metric_name="Relevance",
            input_text=inp,
            generated_output=llm_out,
            criteria="The summary retains important points and details from the source text.",
            steps=[
                "Check whether the facts in 'actual output' contradict any facts in 'input'.",
                "Heavily penalize omission of detail.",
                "Vague language or contradicting opinions are OK."
            ],
            rubric=[
                {"score_range":(0, 2), "expected_outcome":"Factually incorrect."},
                {"score_range":(3, 6), "expected_outcome":"Mostly correct."},
                {"score_range":(7, 9), "expected_outcome":"Correct but missing minor details."},
                {"score_range":(10, 10), "expected_outcome":"100% correct."}
            ]
        )

        response = self.sidewing.chat.completions.create(
                    model=self.model,  # your deployed model name
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": prompt_text}
                    ],
                    temperature=0.3,
                )
        
        print(response.choices[0].message.content.strip())
        return json.loads(response.choices[0].message.content.strip())

    def measure_conciseness_score(self, inp, llm_out):
        prompt_text = self.build_metric_prompt(
            metric_name="Conciseness",
            input_text=inp,
            generated_output=llm_out,
            criteria="The summary is information-dense, does not repeat the same point multiple times, and is not necessarily verbose",
            steps=[
                "Check whether the facts in 'actual output' is smaller than the 'input'",
                "You should also heavily penalize repetition of info",
                "Capturing the important details of the 'input' in the 'actual output' is accepted"
            ],
            rubric=[
                {"score_range":(0,2), "expected_outcome":"Almost the same size as the input itself"},
                {"score_range":(3,6), "expected_outcome":"Repeats most points"},
                {"score_range":(7,9), "expected_outcome":"Fine, but has some unnecessary detail"},
                {"score_range":(10,10), "expected_outcome":"Perfectly information dense and does not repeat any points"},
            ],
        )

        response = self.sidewing.chat.completions.create(
                    model=self.model,  # your deployed model name
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": prompt_text}
                    ],
                    temperature=0.3,
                )
        
        print(response.choices[0].message.content.strip())
        return json.loads(response.choices[0].message.content.strip())
    
    def measure_coherency_score(self, inp, llm_out):
        prompt_text = self.build_metric_prompt(
            metric_name="Coherency",
            input_text=inp,
            generated_output=llm_out,
            criteria="The summary is well structured and easy to follow, not just a jumble of condensed facts",
            steps=[
                "Check whether the facts in 'actual output' is properly structured",
                "You should also heavily penalize big paragraphs of data in 'actual output'",
            ],
            rubric=[
                {"score_range":(0,2), "expected_outcome":"Big Paragraphs and Spelling errors"},
                {"score_range":(3,6), "expected_outcome":"Contains a mixed bag of paragraphs and bullet points"},
                {"score_range":(7,9), "expected_outcome":"Decently Structured"},
                {"score_range":(10,10), "expected_outcome":"Perfectly structured"},
            ],
        )

        response = self.sidewing.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": prompt_text}
                    ],
                    temperature=0.3,
                )
        
        print(response.choices[0].message.content.strip())
        return json.loads(response.choices[0].message.content.strip())
    
    def measure_faithfulness_score(self, inp, llm_out):
        prompt_text = self.build_metric_prompt(
            metric_name="Faithful",
            input_text=inp,
            generated_output=llm_out,
            criteria="The summary does not hallucinate information that is not supported by the source text",
            steps=[
                "Check whether the facts in 'actual output' are not part of the in 'input'",
                "You should also heavily penalize adding unnecessary hallucinated information",
            ],
            rubric=[
                {"score_range":(0,3), "expected_outcome":"Has facts that are not part of input"},
                {"score_range":(4,7), "expected_outcome":"Has extended some of the points mentioned in the input that were not part of the original input"},
                {"score_range":(8,10), "expected_outcome":"Only has the facts that are part of source code"},
            ],
        )

        response = self.sidewing.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": prompt_text}
                    ],
                    temperature=0.3,
                )
        
        print(response.choices[0].message.content.strip())
        return json.loads(response.choices[0].message.content.strip())

    def run_evaluation(self, input, model_summary, csv_path = "evaluations.csv"):
        relevancy = self.measure_relevancy_score(input, model_summary)
        conciseness =self.measure_conciseness_score(input, model_summary)
        coherency = self.measure_coherency_score(input, model_summary)
        faithfulness = self.measure_faithfulness_score(input, model_summary)

        metrics = [relevancy, conciseness, coherency, faithfulness]

        row = {}

        for metric in metrics:
            row[f"Model"] = os.environ["MODEL"]
            row[f"{metric['metric']}_Score"] = metric["score"]
            row[f"{metric['metric']}_Reason"] = metric["reason"]

        new_df = pd.DataFrame([row])
        file_exists = os.path.exists(csv_path)

        new_df.to_csv(csv_path, mode='a', header=not file_exists, index=False)
        print("Evaluation Complete! Results added to CSV file")

    def __call__(self, input, model_summary):
        self.run_evaluation(input, model_summary)

# if __name__ == "__main__":
#     inp = "Dummy Summary"
#     model_summary = "Generate a dummy summary for me"

#     eval = Evaluator()
#     eval(inp, model_summary)
