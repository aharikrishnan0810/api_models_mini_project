import os
import pdfplumber
import google.generativeai as genai 

 
genai.configure(api_key="replace with your API key")  # 

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


def create_prompt(resume_text):
    prompt = f"""
You are an AI resume parser. Extract ALL relevant information from the resume below.

Required fields (return exactly in JSON):
- name (string)
- institution (string, highest or most recent educational institution)
- skills (list of strings, technical and professional skills)
- emails (list of strings)
- phones (list of strings, include country code if present)
- years (list of strings, e.g., graduation years, experience years)

Instructions:
1. RETURN ONLY a single valid JSON object.
2. Do NOT include explanations, extra text, or nested structures.
3. If a field is missing, return "" for strings or [] for lists.
4. Make sure the JSON is syntactically correct.

Resume content:
{resume_text}
"""
    return prompt


def parse_resume_with_gemini(prompt_text):
    model = genai.GenerativeModel("models/gemini-2.5-flash")
    response = model.generate_content(prompt_text)
    return response.text


if __name__ == "__main__":
    pdf_path = r"C:/Users/ahari/OneDrive/Desktop/college file/placement/Hari_Krishnan_A_Resume.pdf"
    resume_text = extract_text_from_pdf(pdf_path)
    
    if resume_text:
        prompt = create_prompt(resume_text)
        output = parse_resume_with_gemini(prompt)
        print(output)  # JSON output
    else:
        print("No text extracted from PDF.")
