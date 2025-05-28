from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from openai import AzureOpenAI
from dotenv import load_dotenv
import pandas as pd
import os
import io

load_dotenv()

app = FastAPI()

# Load environment variables
endpoint = os.getenv("AZURE_ENDPOINT")
deployment = os.getenv("MODEL_NAME")
api_key = os.getenv("OPENAI_API_KEY")
api_version = os.getenv("API_VERSION")

# Initialize Azure OpenAI client
client = AzureOpenAI(
    api_key=api_key,
    api_version=api_version,
    azure_endpoint=endpoint,
)


@app.post("/analyze")
async def analyze_csv(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")

    try:
        content = await file.read()
        df = pd.read_csv(io.StringIO(content.decode("ISO-8859-1")))

        # Split into chunks
        chunk_size = 50
        chunks = [df[i:i+chunk_size] for i in range(0, len(df), chunk_size)]
        all_summaries = []

        for i, chunk in enumerate(chunks):
            table_text = chunk.to_markdown(index=False)

            response = client.chat.completions.create(
                model=deployment,
                messages=[
                    {"role": "system", "content": "You are a helpful business analyst."},
                    {"role": "user", "content": f"Here is a sales report:\n{table_text}\nPlease summarize key sales insights and highlight trends."}
                ],
                max_tokens=1000,
                temperature=0.7,
                top_p=1.0,
            )

            all_summaries.append(response.choices[0].message.content)

        # Final summary
        final_response = client.chat.completions.create(
            model=deployment,
            messages=[
                {"role": "user", "content": "Summarize the following insights:\n\n" + "\n\n".join(all_summaries)}
            ],
            max_tokens=1000,
            temperature=0.7,
            top_p=1.0,
        )

        final_summary = final_response.choices[0].message.content
        return JSONResponse(content={"summary": final_summary})

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))