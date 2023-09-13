import os
import time
import openai
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

gender_list = ["male", "female"]
age_list = [6, 18, 25, 32, 48, 60, 70, 80, 90, 99]
superpower_list = ["flight", "telepathy", "telekinesis", "x-ray vision", "invisibility", "immortality",
                   "mind reading", "turn lead into gold", "harness electrical power", "walk on liquid"]

prompt_format = "Imagine a complete and detailed description of a {age}-year-old {gender} " \
                "fictional character who has the superpower of {superpower}. " \
                "Write out the entire description in a maximum of 100 words in great detail:"
sub_prompt_format = "{age}, {gender}, {superpower}"

training_data = pd.DataFrame()
for age in age_list:
    for gender in gender_list:
        for superpower in superpower_list:
            for attempt in range(5):
                try:
                    prompt = prompt_format.format(age=age, gender=gender, superpower=superpower)
                    sub_prompt = sub_prompt_format.format(age=age, gender=gender, superpower=superpower)

                    completion_response = openai.ChatCompletion.create(
                        model='gpt-3.5-turbo',
                        messages=[{'role': 'user', 'content': prompt}],
                    )

                    training_data = pd.concat([
                        training_data,
                        pd.DataFrame([{
                            'age': age,
                            'gender': gender,
                            'superpower': superpower,
                            'prompt': prompt,
                            'sub_prompt': sub_prompt,
                            'response_text': completion_response['choices'][0]['message']['content'],
                            'finish_reason': completion_response['choices'][0]['finish_reason']
                        }])
                    ], axis=0, ignore_index=True)

                    time.sleep(20)

                except openai.error.OpenAIError as exception:
                    if isinstance(exception, (openai.error.Timeout,
                                              openai.error.APIError,
                                              openai.error.RateLimitError,
                                              openai.error.APIConnectionError,
                                              openai.error.ServiceUnavailableError)) and attempt < 4:
                        time.sleep(attempt * 3)
                        continue
                    raise exception

training_data.to_csv('training_data.csv')
