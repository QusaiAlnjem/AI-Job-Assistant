import os
import json
from pdfminer.high_level import extract_text
from openai import OpenAI
from django.conf import settings
import docx

client = OpenAI(api_key=settings.LLM_API_KEY, base_url=settings.ENDPOINT)

def extract_text_from_file(file_path):
    ext = os.path.splitext(file_path)[1].lower()

    try:
        if ext == '.pdf':
            return extract_text(file_path)

        elif ext == '.docx':
            doc = docx.Document(file_path)
            return "\n".join([para.text for para in doc.paragraphs])

    except Exception as e:
        print(f"Error extracting file: {e}")
        return None

def parse_resume_with_ai(resume_text):
    """
    Sends the raw text to the LLM to get structured JSON.
    """
    prompt = f"""
    You are an expert recruiter. Extract the following from this resume text:
    1. List of technical skills.
    2. Years of experience (total).
    3. Job titles held.
    4. A short professional summary.

    Return ONLY valid JSON in this format:
    {{
        "skills": ["python", "django", ...],
        "years_experience": 3,
        "job_titles": ["Junior Dev", "Backend Engineer"],
        "summary": "..."
    }}

    Resume Text:
    {resume_text[:4000]}
    """

    try:
        response = client.chat.completions.create(
            model=settings.MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a JSON extractor."},
                {"role": "user", "content": prompt}
            ],
            response_format={ "type": "json_object" } # Critical: Forces JSON output
        )
        
        # Parse the string response into a real Python dictionary
        data = json.loads(response.choices[0].message.content)
        return data

    except Exception as e:
        print(f"AI Error: {e}")
        return None