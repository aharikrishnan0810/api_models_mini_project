from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import os
import re
import json
import pdfplumber
import google.generativeai as genai

app = FastAPI()

# Configure Gemini API
genai.configure(api_key="put_your_api")
MODEL_NAME = "models/gemini-2.5-flash"

def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print("Error extracting PDF:", e)
    return text

def create_prompt(paper_text):
    prompt = f"""
You are an AI research paper parser. Extract ALL relevant information from the research paper below.

Required fields (return exactly in JSON):
- title (string)
- authors (list of strings)
- publish_date (string)
- top_5_references (list of strings)
- introduction_summary (list of 5 points summarizing the introduction)
- conclusion_summary (list of points summarizing the conclusion)

Instructions:
1. RETURN ONLY a single valid JSON object.
2. Do NOT include explanations or extra text.
3. If a field is missing, return "" for strings or [] for lists.
4. Make sure the JSON is syntactically correct.

Research Paper Content:
{paper_text}
"""
    return prompt

def parse_paper_with_gemini(prompt_text):
    model = genai.GenerativeModel(MODEL_NAME)
    response = model.generate_content(prompt_text)
    return response.text

def clean_gemini_output(response_text: str):
    cleaned = re.sub(r"^```json\s*|\s*```$", "", response_text.strip(), flags=re.MULTILINE)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return {"raw_text": cleaned}

@app.post("/parse_paper/")
async def parse_paper(file: UploadFile = File(...)):
    # Save uploaded PDF temporarily
    temp_file_path = f"temp_{file.filename}"
    with open(temp_file_path, "wb") as f:
        f.write(await file.read())
    
    # Extract text
    paper_text = extract_text_from_pdf(temp_file_path)
    os.remove(temp_file_path)

    if not paper_text:
        return JSONResponse(status_code=400, content={"error": "No text extracted from PDF."})
    
    # Generate prompt and parse
    prompt = create_prompt(paper_text)
    output = parse_paper_with_gemini(prompt)

    # Clean Gemini output
    parsed_json = clean_gemini_output(output)

    return JSONResponse(content={"parsed_paper": parsed_json})
