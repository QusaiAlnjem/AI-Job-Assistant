import { ENDPOINTS, getToken } from './config.js';

// Global variable to store if we have a resume
let hasResume = false;

document.addEventListener('DOMContentLoaded', async () => {
    const token = getToken();
    if (!token) { window.location.href = 'login.html'; return; }

    // 1. Check Resume Status immediately on load
    await checkResumeStatus(token);

    // 2. Setup Conditional Location Logic
    const jobTypeSelect = document.getElementById('jobType');
    const locationGroup = document.getElementById('location-group');
    const locationInput = document.getElementById('location');

    jobTypeSelect.addEventListener('change', (e) => {
        if (e.target.value === 'remote') {
            locationGroup.classList.add('hidden');
            locationInput.value = ''; // Clear location if remote
            locationInput.removeAttribute('required');
        } else {
            locationGroup.classList.remove('hidden');
            locationInput.setAttribute('required', 'true'); // Make location required if onsite/hybrid
        }
    });
});

async function checkResumeStatus(token) {
    const resumeSection = document.getElementById('resume-section');
    const searchForm = document.getElementById('searchForm');
    
    // 1. Start with Loading State
    resumeSection.innerHTML = `<div class="spinner"></div><p>Checking profile...</p>`;
    resumeSection.classList.remove('hidden');

    try {
        const response = await fetch(ENDPOINTS.RESUMES, {
            headers: { 'Authorization': `Token ${token}` }
        });
        const data = await response.json();
        
        resumeSection.innerHTML = ''; // CLEAR the spinner explicitly

        if (response.ok && data.length > 0) {
            // Case A: Resume Exists
            hasResume = true;
            resumeSection.innerHTML = `
                <div style="padding: 10px; background: #e6fffa; border: 1px solid #b2f5ea; border-radius: 6px; color: #234e52;">
                    <i class="fas fa-check-circle"></i> <strong>Resume Ready:</strong> Using your latest upload.
                </div>`;
            searchForm.classList.remove('hidden'); // Show form
        } else {
            // Case B: Empty List (Show Upload UI)
            hasResume = false;
            // Inject the Upload Form directly
            resumeSection.innerHTML = `
                <div style="padding: 15px; background: #fff5f5; border: 1px solid #fed7d7; border-radius: 6px; text-align: left;">
                    <strong style="color: #c53030;"><i class="fas fa-exclamation-circle"></i> No Resume Found</strong>
                    <p style="margin: 5px 0 10px; font-size: 0.9em;">You must upload a resume before scanning.</p>
                    
                    <div style="display: flex; gap: 10px; align-items: center;">
                        <input type="file" id="resumeUpload" accept=".pdf,.docx">
                        <button id="quickUploadBtn" class="btn-small">Upload</button>
                    </div>
                </div>
            `;
            // IMPORTANT: Attach the event listener NOW, because we just created the button
            document.getElementById('quickUploadBtn').addEventListener('click', (e) => uploadResume(e, token));
            
            // Do NOT show searchForm yet (force them to upload first)
        }
        // === FIX ENDS HERE ===

    } catch (error) {
        console.error("Resume Check Error", error);
        resumeSection.innerHTML = `<p style="color:red">Error loading profile.</p>`;
    }
}
    
async function uploadResume(e, token) {
    e.preventDefault(); // Stop page refresh
    
    const fileInput = document.getElementById('resumeUpload');
    const file = fileInput.files[0];
    
    if (!file) { alert("Please select a file first."); return; }

    const formData = new FormData();
    formData.append('file', file); // Make sure your Django Model expects 'file'

    // Change button text to show it's working
    e.target.innerText = "Uploading...";
    e.target.disabled = true;

    try {
        const response = await fetch(ENDPOINTS.RESUMES, {
            method: 'POST',
            headers: { 
                'Authorization': `Token ${token}` 
            },
            body: formData
        });

        if (response.ok) {
            alert("Upload Success!");
            location.reload(); // Refresh page to see the "Resume Ready" state
        } else {
            const err = await response.json();
            alert("Upload Failed: " + JSON.stringify(err));
            e.target.innerText = "Upload"; // Reset button
            e.target.disabled = false;
        }
    } catch (error) {
        alert("Network Error");
        console.error(error);
    }
}

// 3. The Main Scan Function
document.getElementById('searchForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const title = document.getElementById('jobTitle').value;
    const type = document.getElementById('jobType').value;
    const loc = document.getElementById('location').value;

    // UI: Show loading
    document.getElementById('searchForm').classList.add('hidden');
    document.getElementById('resume-section').classList.add('hidden');
    document.getElementById('loading-state').classList.remove('hidden');
    document.getElementById('error-message').classList.add('hidden');

    try {
        const token = getToken();
        
        // 1. Send separated fields
        const payload = { 
            title: title,
            job_type: type,
            location: loc 
        };

        const response = await fetch(ENDPOINTS.JOB_SEARCH, { 
            method: 'POST',
            headers: {
                'Authorization': `Token ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (response.ok) {
            // Check if we actually got matches
            if (Array.isArray(data) && data.length > 0) {
                window.location.href = 'results.html'; 
            } else {
                throw new Error(data.message || "AI scanned the web but found no jobs matching your resume criteria.");
            }
        } else {
            throw new Error(data.error || 'Search failed.');
        }

    } catch (error) {
        console.error(error);
        document.getElementById('loading-state').classList.add('hidden');
        document.getElementById('searchForm').classList.remove('hidden');
        document.getElementById('resume-section').classList.remove('hidden');
        
        const errDiv = document.getElementById('error-message');
        errDiv.textContent = error.message;
        errDiv.classList.remove('hidden');
    }
});