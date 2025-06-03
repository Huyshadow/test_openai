import pandas as pd
import os
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv() 

endpoint = os.getenv("AZURE_ENDPOINT")
model_name = os.getenv("MODEL_NAME")
deployment = os.getenv("MODEL_NAME")
subscription_key = os.getenv("OPENAI_API_KEY")
api_version = os.getenv("API_VERSION")

df = pd.read_csv("synthetic_beverage_sales_data.csv", encoding='ISO-8859-1')  

chunk_size = 50
chunks = [df[i:i+chunk_size] for i in range(0, df.shape[0], chunk_size)]

all_summaries = []

client = AzureOpenAI(
    api_version=api_version,
    azure_endpoint=endpoint,
    api_key=subscription_key,
)

for chunk in chunks:
    table_text = chunk.to_markdown(index=False)

    response = client.chat.completions.create(
    messages=[
        {
            "role": "system", 
            "content": "You are a helpful assistant."},
        {
            "role": "user",
           "content": f"Here is a business report:\n{table_text}\nPlease summarize key sales insights and highlight trends.",
        }
    ],
    max_tokens=1000,
    temperature=1.0,
    top_p=1.0,
    model=deployment
    )
    
    all_summaries.append(response.choices[0].message.content)
    print(response.choices[0].message.content)
    print("--------------------------------------------------")


final_summary = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "user", "content": "Summarize the following insights:\n\n" + "\n\n".join(all_summaries)}
    ]
)