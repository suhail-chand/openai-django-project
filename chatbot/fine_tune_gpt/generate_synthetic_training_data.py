import os
import time
import openai
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

gender_list = ["male", "female"]
age_list = [6, 13, 18, 24, 30, 42, 50, 60, 75, 90]
disease_list = ["flu", "common cold", "mononucleosis", "dengue", "malaria", "anemia",
                "alcoholism", "tuberculosis", "herpes simplex", "migraine"]

prompt_format = ("Generate a structured and comprehensive treatment plan for a "
                 "{age} year old {gender} diagnosed with {disease}.")
sub_prompt_format = "{age}, {gender}, {disease}"

training_data = pd.DataFrame()
for age in age_list:
    for gender in gender_list:
        for disease in disease_list:
            for attempt in range(5):
                try:
                    prompt = prompt_format.format(age=age, gender=gender, disease=disease)
                    sub_prompt = sub_prompt_format.format(age=age, gender=gender, disease=disease)

                    completion_response = openai.ChatCompletion.create(
                        model='gpt-3.5-turbo',
                        messages=[{'role': 'user', 'content': prompt}],
                    )

                    training_data = pd.concat([
                        training_data,
                        pd.DataFrame([{
                            'age': age,
                            'gender': gender,
                            'disease': disease,
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
