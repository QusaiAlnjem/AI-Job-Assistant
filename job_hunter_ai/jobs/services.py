from .models import Job, JobMatch
from .scraper import scrape_weworkremotely
import json
from openai import OpenAI
from django.conf import settings

def search_and_save_jobs(job_query):
    """
    1. Calls the scraper.
    2. Saves results to the DB.
    3. Returns the list of Job objects created/found.
    """
    raw_jobs = scrape_weworkremotely(job_query)
    saved_jobs = []

    for j in raw_jobs:
        # update_or_create prevents duplicates based on the URL
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
    Act as a Hiring Manager. Compare this candidate to the job description.
    
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