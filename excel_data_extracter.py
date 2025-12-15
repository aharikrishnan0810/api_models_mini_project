#import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel
import requests
import os
from dotenv import load_dotenv

# -------------------------------
# Load API key from .env
# -------------------------------
# -------------------------------
API_KEY = "YOUR_GEMINI_API_KEY_HERE"  # <-- replace with your actual API key
URL = "https://api.generative.ai/v1/models/gemini-2.5-flash:generate"
# -------------------------------
# Load Excel
# -------------------------------
EXCEL_PATH = r"C:\\Users\\ahari\\OneDrive\Desktop\\icanio Intern\\project\\intern_communication_data.xlsx"
df = pd.read_excel(EXCEL_PATH)
skills = ["Pronunciation Avg", "Grammar Avg", "Vocabulary Avg", "Fluency Avg", "Confidence Avg", "Body Language Avg"]

# -------------------------------
# Initialize FastAPI
# -------------------------------
app = FastAPI(title="Intern Communication AI System (Gemini)")

# -------------------------------
# Request model
# -------------------------------
class ReportRequest(BaseModel):
    name: str

# -------------------------------
# Function to call Gemini
# -------------------------------
def call_gemini(prompt):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "prompt": prompt,
        "temperature": 0.7,
        "max_output_tokens": 500
    }
    response = requests.post(URL, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()["candidates"][0]["content"]
    else:
        return f"Error: {response.status_code} - {response.text}"


# -------------------------------
# API Endpoint
# -------------------------------
@app.post("/report")
def get_report(request: ReportRequest):
    name = request.name.strip().lower()

    # Overall report
    if name == "overall":
        overall_avg = df[skills].mean()
        prompt = f"""
Analyze the overall performance of interns:

Pronunciation: {overall_avg['Pronunciation Avg']:.2f}
Grammar: {overall_avg['Grammar Avg']:.2f}
Vocabulary: {overall_avg['Vocabulary Avg']:.2f}
Fluency: {overall_avg['Fluency Avg']:.2f}
Confidence: {overall_avg['Confidence Avg']:.2f}
Body Language: {overall_avg['Body Language Avg']:.2f}

Provide JSON with: strengths (list), weaknesses (list), recommendations (list), motivational_note (string)
"""
        ai_response = call_gemini(prompt)
        return {"type": "overall", "ai_text": ai_response}

    # Individual intern report
    df['Normalized Name'] = df['Intern Name'].apply(lambda x: x.strip().lower())
    row = df[df['Normalized Name'] == name]

    if not row.empty:
        row_data = row.iloc[0]
        prompt = f"""
Analyze the following intern:

Intern Name: {row_data['Intern Name']}
Pronunciation: {row_data['Pronunciation Avg']}
Grammar: {row_data['Grammar Avg']}
Vocabulary: {row_data['Vocabulary Avg']}
Fluency: {row_data['Fluency Avg']}
Confidence: {row_data['Confidence Avg']}
Body Language: {row_data['Body Language Avg']}

Provide JSON with: strengths (list), weaknesses (list), recommendations (list), motivational_note (string)
"""
        ai_response = call_gemini(prompt)
        return {"type": "individual", "name": row_data['Intern Name'], "ai_text": ai_response}

    return {"error": "Intern not found"}
