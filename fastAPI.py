from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import pandas as pd
import os
from dotenv import load_dotenv
from openai import AzureOpenAI
import io

load_dotenv()

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for development; change in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load Azure OpenAI credentials
endpoint = os.getenv("AZURE_ENDPOINT")
deployment = os.getenv("MODEL_NAME")
subscription_key = os.getenv("OPENAI_API_KEY")
api_version = os.getenv("API_VERSION")

client = AzureOpenAI(
    api_version=api_version,
    azure_endpoint=endpoint,
    api_key=subscription_key,
)


@app.post("/analyze")
async def analyze_sales_data(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")

    # Read uploaded CSV file
    content = await file.read()
    df = pd.read_csv(io.StringIO(content.decode("ISO-8859-1")))

    # Chunk data
    chunk_size = 50
    chunks = [df[i : i + chunk_size] for i in range(0, df.shape[0], chunk_size)]

    all_summaries = []

    # for chunk in chunks:
    #   table_text = chunk.to_markdown(index=False)
    for i in range(min(3, len(chunks))):  # Process first 3 chunks
        table_text = chunks[i].to_markdown(index=False)

        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful V4AB assistant business analysis.",
                },
                {
                    "role": "user",
                    "content": f"""
                        You are a business data analyst. Analyze the following sales dataset and extract meaningful business insights in a structured format. Focus on the following areas:

                        1. Sales Growth Trends
                        2. Product Line Performance
                        3. Customer Regional Distribution
                        4. Deal Size Breakdown
                        5. Order Status Insights
                        6. Customer Type Segmentation
                        7. Yearly or Quarterly Performance
                        8. Regional/Territory-wise Opportunities

                        Here is the dataset (in markdown table format):

                        {table_text}

                        Please provide a clear and concise summary of the key business insights grouped by the areas above. Use bullet points for each section and quantify findings when possible.
                    """,
                },
            ],
            max_tokens=4000,
            temperature=1.0,
            top_p=1.0,
            model=deployment,
        )

        all_summaries.append(response.choices[0].message.content)

    # Generate final summary
    final_response = client.chat.completions.create(
        max_tokens=4000,
        temperature=1.0,
        top_p=1.0,
        model=deployment,
        messages=[
            {
                "role": "system",
                "content": "You are a business analyst assistant. Your job is to consolidate insights from multiple partial analyses and suggest visual summaries.",
            },
            {
                "role": "user",
                "content": (
                    "Based on the following multiple insight summaries, generate a consolidated business insight report. "
                    "Then suggest appropriate visualizations (charts or tables) that could effectively present the information to a business team:\n\n"
                    + "\n\n".join(all_summaries)
                ),
            },
        ],
    )

    return JSONResponse(content={"summary": final_response.choices[0].message.content})
