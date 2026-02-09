import { ENDPOINTS, getToken } from './config.js';

document.addEventListener('DOMContentLoaded', loadProfile);

async function loadProfile() {
    const token = getToken();
    if (!token) window.location.href = 'login.html';

    try {
        const response = await fetch(ENDPOINTS.RESUMES, {
            headers: { 'Authorization': `Token ${token}` }
        });

        if (response.ok) {
            const resumes = await response.json();
            
            const resumeSection = document.getElementById('current-resume-section');
            const noResumeMsg = document.getElementById('no-resume-message');

            if (resumes.length > 0) {
                // SHOW Resume Section, HIDE Message
                const latestResume = resumes[0];
                
                resumeSection.style.display = 'block'; 
                noResumeMsg.style.display = 'none';      
                
                const filename = latestResume.file.split('/').pop();
                document.getElementById('resume-name').textContent = filename;
                document.getElementById('resume-date').textContent = "Uploaded: " + new Date(latestResume.uploaded_at).toLocaleDateString();
            } else {
                // HIDE Resume Section, SHOW Message
                resumeSection.style.display = 'none';    
                noResumeMsg.style.display = 'block';   
            }
        }
    } catch (error) {
        console.error("Error loading profile:", error);
    }
}

// Upload Logic (Same as before)
document.getElementById('resumeForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const fileInput = document.getElementById('resumeFile');
    const statusMsg = document.getElementById('upload-status');
    const btn = e.target.querySelector('button');
    const token = getToken();

    if (!fileInput.files[0]) { alert("Please select a file."); return; }

    btn.disabled = true;
    btn.innerText = "Uploading...";
    statusMsg.innerText = "";

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    try {
        const response = await fetch(ENDPOINTS.RESUMES, {
            method: 'POST',
            headers: { 'Authorization': `Token ${token}` },
            body: formData
        });

        if (response.ok) {
            statusMsg.innerText = "Success! Reloading...";
            statusMsg.style.color = "green";
            setTimeout(() => location.reload(), 1000);
        } else {
            const err = await response.json();
            throw new Error(JSON.stringify(err));
        }
    } catch (error) {
        statusMsg.innerText = "Error: " + error.message;
        btn.disabled = false;
        btn.innerText = "Upload & Analyze";
    }
});