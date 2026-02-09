import { ENDPOINTS, getToken } from './config.js';

document.addEventListener('DOMContentLoaded', async () => {
    const container = document.getElementById('results-container');
    const token = getToken();

    if (!token) window.location.href = 'login.html';

    try {
        const response = await fetch(ENDPOINTS.JOB_MATCHES, {
            headers: { 'Authorization': `Token ${token}` }
        });

        if (!response.ok) throw new Error("Failed to load matches");

        const matches = await response.json();
        container.innerHTML = ''; 

        if (matches.length === 0) {
            container.innerHTML = `<p>No matches found yet. Try <a href="scanner.html">scanning</a>.</p>`;
            return;
        }

        matches.forEach(match => {
            const card = createJobCard(match);
            container.appendChild(card);
        });

    } catch (error) {
        console.error(error);
        container.innerHTML = `<p style="color:red">Error loading results.</p>`;
    }
});

function createJobCard(match) {
    const div = document.createElement('div');
    div.className = 'job-card';

    // Handle Score Color
    let scoreClass = 'low';
    if (match.match_score >= 80) scoreClass = 'high';
    else if (match.match_score >= 50) scoreClass = 'medium';

    // Handle Missing Keywords (Assuming AI stores them in ai_analysis)
    const analysis = match.ai_analysis || {};
    const missing = analysis.missing_keywords || [];
    
    // Create HTML for missing keywords (limit to 3)
    const missingHtml = missing.slice(0, 3)
        .map(k => `<span class="keyword missing">${k}</span>`)
        .join('');

    div.innerHTML = `
        <div class="match-badge ${scoreClass}">${match.match_score}% Match</div>
        <div class="company-name">${match.job.company}</div>
        <div class="job-title">${match.job.title}</div>
        
        <div class="keywords">
            ${missing.length > 0 ? '<span>Missing:</span>' + missingHtml : '<span style="color:green; font-size:0.8rem">Great Match!</span>'}
        </div>

        <p style="font-size: 0.9rem; color: #666; margin-bottom: 15px;">
            ${analysis.advice || "Click apply to see more."}
        </p>

        <div class="card-actions">
            <a href="${match.job.url}" target="_blank" class="btn btn-apply" style="display:block; text-align:center; background: var(--primary); color: white; padding: 10px; border-radius: 6px; text-decoration: none;">Apply Now</a>
        </div>
    `;
    return div;
}