import os
import openai
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Import training data from .csv file
training_data = pd.read_csv("chatbot/fine_tune/training_data.csv")

# Convert the data into the conversational chat format
training_data['messages'] = training_data[['sub_prompt', 'response_text']].apply(
    lambda x: [{'role': 'user', 'content': x['sub_prompt']},
               {'role': 'assistant', 'content': x['response_text']}], axis=1)

# Write JSONL formatted data into a file
pd.DataFrame(training_data['messages']).to_json(path_or_buf='chatbot/fine_tune/training_file.jsonl',
                                                orient='records',
                                                lines=True)

# Upload the training file
training_file = openai.File.create(
    file=open("chatbot/fine_tune/training_file.jsonl", "rb"),
    purpose='fine-tune'
)

# Create fine-tuning job
openai.FineTuningJob.create(model='gpt-3.5-turbo',
                            training_file=training_file['id'],
                            hyperparameters={'n_epochs': 2})

print(openai.FineTuningJob.list())
