import { ENDPOINTS, getToken } from './config.js';
import { logout } from './auth.js';

// 1. Initialize
document.addEventListener('DOMContentLoaded', async () => {
    const token = getToken();
    if (!token) {
        window.location.href = 'login.html';
        return;
    }

    // Set User Name (Stored in localStorage during login)
    const username = localStorage.getItem('username') || 'User';
    document.getElementById('user-name').textContent = username;

    // Attach Logout
    document.getElementById('logoutBtn').addEventListener('click', logout);

    // Fetch Data
    loadDashboardData(token);
});

// 2. Fetch Logic
async function loadDashboardData(token) {
    try {
        const response = await fetch(`${ENDPOINTS.JOB_MATCHES}?ordering=-created_at`, {
            headers: { 'Authorization': `Token ${token}` }
        });

        if (!response.ok) throw new Error("Failed to fetch jobs");

        const matches = await response.json();
        
        // Update the UI
        updateStats(matches);
        renderTable(matches, token);

    } catch (error) {
        console.error("Dashboard Error:", error);
        document.getElementById('job-list').innerHTML = `<tr><td colspan="6" style="color:red; text-align:center;">Error loading data.</td></tr>`;
    }
}

// 3. Stats Logic
function updateStats(matches) {
    const total = matches.length;
    // Count how many have specific statuses
    const interviews = matches.filter(m => m.status === 'INTERVIEW').length;
    const offers = matches.filter(m => m.status === 'OFFER').length;

    // Animate numbers (simple text update)
    document.getElementById('stat-total').innerText = total;
    document.getElementById('stat-interview').innerText = interviews;
    document.getElementById('stat-offer').innerText = offers;
}

// 4. Table Logic
function renderTable(matches, token) {
    const tbody = document.getElementById('job-list');
    tbody.innerHTML = ''; // Clear "Loading..."

    if (matches.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; padding: 20px;">No jobs found. <a href="scanner.html" style="color: var(--primary);">Start a new scan</a></td></tr>`;
        return;
    }

    matches.forEach(match => {
        const tr = document.createElement('tr');
        
        // Date Formatting
        const dateObj = new Date(match.created_at);
        const dateStr = dateObj.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });

        // Score Color Logic
        let scoreClass = 'low';
        if (match.match_score >= 80) scoreClass = 'high';
        else if (match.match_score >= 50) scoreClass = 'medium';

        tr.innerHTML = `
            <td><strong>${match.job.company}</strong></td>
            <td>${match.job.title}</td>
            <td>${dateStr}</td>
            <td><span class="score ${scoreClass}">${match.match_score}%</span></td>
            <td>${createStatusDropdown(match)}</td>
            <td>
                <a href="results.html?id=${match.id}" class="btn-small">Details</a>
            </td>
        `;

        // Add event listener for the dropdown change
        const select = tr.querySelector('select');
        select.addEventListener('change', (e) => updateJobStatus(match.id, e.target.value, token));

        tbody.appendChild(tr);
    });
}

// 5. Helper: Create the Dropdown HTML
function createStatusDropdown(match) {
    const statuses = {
        'NEW': 'New Match',
        'APPLIED': 'Applied',
        'INTERVIEW': 'Interviewing',
        'OFFER': 'Offer',
        'REJECTED': 'Rejected'
    };

    let options = '';
    for (const [key, label] of Object.entries(statuses)) {
        const selected = match.status === key ? 'selected' : '';
        options += `<option value="${key}" ${selected}>${label}</option>`;
    }

    // Return the select element with a class based on current status (for coloring)
    return `<select class="status-select ${match.status.toLowerCase()}">${options}</select>`;
}

// 6. Action: Update Status via API
async function updateJobStatus(id, newStatus, token) {
    try {
        const response = await fetch(`${ENDPOINTS.JOB_MATCHES}${id}/`, {
            method: 'PATCH',
            headers: {
                'Authorization': `Token ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ status: newStatus })
        });

        if (response.ok) {
            console.log(`Status updated to ${newStatus}`);
            // Optional: Reload data to update stats immediately
            loadDashboardData(token); 
        } else {
            alert("Failed to update status.");
        }
    } catch (error) {
        console.error("Update failed", error);
    }
}