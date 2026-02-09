import { API_BASE_URL, getToken } from './config.js';

const CHECK_ENDPOINT = `${API_BASE_URL}/jobs/check/`;
const RESUME_ENDPOINT = `${API_BASE_URL}/resumes/`;

document.addEventListener('DOMContentLoaded', async () => {
    const token = getToken();
    if (!token) window.location.href = 'login.html';

    // Check Resume Exists
    try {
        const response = await fetch(RESUME_ENDPOINT, { headers: { 'Authorization': `Token ${token}` } });
        const resumes = await response.json();
        
        if (resumes.length > 0) {
            document.getElementById('resume-section').style.display = 'block';
            document.getElementById('no-resume-alert').style.display = 'none';
        } else {
            document.getElementById('resume-section').style.display = 'none';
            document.getElementById('no-resume-alert').style.display = 'block';
            document.getElementById('checkBtn').disabled = true;
        }
    } catch (e) { console.error(e); }
});

document.getElementById('checkForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const title = document.getElementById('jobTitle').value || "Unknown Role";
    const desc = document.getElementById('jobDesc').value;
    const token = getToken();
    const loadingState = document.getElementById('loading-state');
    const resultArea = document.getElementById('result-area');
    const btn = document.getElementById('checkBtn');

    // UI Updates: Show Loading, Hide Results
    resultArea.style.display = 'none'; 
    loadingState.style.display = 'block'; 
    btn.disabled = true;

    try {
        const response = await fetch(CHECK_ENDPOINT, {
            method: 'POST',
            headers: {
                'Authorization': `Token ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ title: title, description: desc })
        });

        const match = await response.json();

        if (response.ok) {
            displayResult(match);
        } else {
            alert("Error: " + (match.error || "Analysis failed"));
        }

    } catch (error) {
        console.error(error);
        alert("Network Error");
    } finally {
        // Hide Loading, Re-enable button
        loadingState.style.display = 'none';
        btn.disabled = false;
    }
});

function displayResult(match) {
    const box = document.getElementById('result-area');
    const titleEl = document.getElementById('res-title');
    const scoreValEl = document.getElementById('res-score');
    const scoreCircle = document.getElementById('score-circle');
    const keyEl = document.getElementById('res-keywords');
    const missingSection = document.getElementById('missing-section');
    const adviceListEl = document.getElementById('res-advice-list');

    // 1. Set Title & Score
    titleEl.innerText = match.job.title;
    scoreValEl.innerText = match.match_score + "%";
    
    // Set Circle Color
    if(scoreCircle) {
        scoreCircle.className = 'score-circle'; 
        if (match.match_score >= 80) scoreCircle.classList.add('high');
        else if (match.match_score >= 50) scoreCircle.classList.add('medium');
        else scoreCircle.classList.add('low');
    }

    // --- AI ANALYSIS DATA ---
    const analysis = match.ai_analysis || {};

    const missing = analysis.missing_skills || analysis.missing_keywords || [];
    
    if (missing.length === 0) {
        if(missingSection) missingSection.style.display = 'none';
    } else {
        if(missingSection) missingSection.style.display = 'block';
        keyEl.innerHTML = missing.map(skill => 
            `<span class="keyword-tag">${skill}</span>`
        ).join('');
    }

    // 3. Handle Advice (Corrected Logic: Array Handling)
    const rawAdvice = analysis.advice;
    let tips = [];

    if (Array.isArray(rawAdvice)) {
        tips = rawAdvice;
    } else if (typeof rawAdvice === 'string') {
        tips = rawAdvice.split(/\.|\n/).filter(t => t.trim().length > 5);
    } else {
        tips = ["No specific advice generated."];
    }

    // Render the List
    adviceListEl.innerHTML = tips.map(tip => 
        `<li>${tip.replace(/^\d+\.\s*/, '').trim()}</li>`
    ).join('');

    // 4. Reveal Result
    box.style.display = 'block';
}