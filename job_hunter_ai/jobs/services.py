from .models import Job, JobMatch
from .scraper import scrape_weworkremotely
import json
from openai import OpenAI
from django.conf import settings

def search_and_save_jobs(title, location, job_type):
    raw_jobs = scrape_weworkremotely(title, location, job_type)
    
    saved_jobs = []
    for j in raw_jobs:
        job_obj, created = Job.objects.update_or_create(
            url=j['url'],
            defaults={
                'title': j['title'],
                'company': j['company'],
                'description': j['description'],
                'source': j['source']
            }
        )
        saved_jobs.append(job_obj)
    return saved_jobs

client = OpenAI(api_key=settings.LLM_API_KEY, base_url=settings.ENDPOINT)
def analyze_job_match(user, resume, job):
    """
    1. Constructs a prompt with the Resume + Job Description.
    2. Asks AI for a match score (0-100) and advice.
    3. Saves the result to JobMatch.
    """
    if JobMatch.objects.filter(user=user, job=job).exists():
        print(f"Match already exists for {job.title}")
        return JobMatch.objects.get(user=user, job=job)

    print(f"Analyzing match: {job.title} vs {user.username}'s Resume...")

    prompt = f"""
    Role:
    Hiring Manager Task: Evaluate the Candidate's Resume against the Job Description.
    Constraint:
    Be lenient regarding software specifics.
    Prioritize underlying skills over exact tool matches (e.g., treat DaVinci Resolve proficiency as applicable for Premiere Pro requirements).
    Assume minor resume gaps may be due to brevity.
    
    JOB DESCRIPTION:
    {job.description[:3000]} 

    CANDIDATE RESUME (JSON):
    {json.dumps(resume.structured_data)}

    OUTPUT IN JSON FORMAT ONLY:
    {{
        "match_score": <integer 0-100>,
        "missing_skills": ["skill1", "skill2"],
        "advice": ["tip 1", "tip 2"],
        "why_match": "One sentence summary of why they fit or don't fit."
    }}
    """

    try:
        response = client.chat.completions.create(
            model=settings.MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a precise job matching AI."},
                {"role": "user", "content": prompt}
            ],
            response_format={ "type": "json_object" }
        )
        
        # Parse AI Result
        ai_content = json.loads(response.choices[0].message.content)
        
        # Save to Database
        match = JobMatch.objects.create(
            user=user,
            job=job,
            resume=resume,
            match_score=ai_content.get('match_score', 0),
            ai_analysis=ai_content # Stores the tips, missing skills, etc.
        )
        
        return match

    except Exception as e:
        print(f"AI Error: {e}")
        return None