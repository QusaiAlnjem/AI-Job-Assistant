import { ENDPOINTS } from './config.js';

export async function login(username, password) {
    try {
        const response = await fetch(ENDPOINTS.LOGIN, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Save Token & User Info
            localStorage.setItem('auth_token', data.token);
            localStorage.setItem('username', data.username);
            window.location.href = 'dashboard.html';
        } else {
            throw new Error(data.error || 'Login failed');
        }
    } catch (error) {
        alert(error.message); // Simple alert for now
    }
}

export async function signup(username, email, password) {
    try {
        const captchaToken = grecaptcha.getResponse();

        if (captchaToken.length === 0) {
            throw new Error("Please complete the CAPTCHA.");
        }

        // Make sure ENDPOINTS.SIGNUP is defined in your config.js!
        const response = await fetch(ENDPOINTS.SIGNUP, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, email, password, captchaToken })
        });

        const data = await response.json();

        if (response.ok) {
            // OPTION A: Auto-login after signup (If backend returns a token)
            if (data.token) {
                localStorage.setItem('auth_token', data.token);
                localStorage.setItem('username', username);
                window.location.href = 'dashboard.html';
            } 
            // OPTION B: Redirect to login (If backend just says "Created")
            else {
                alert("Account created! Please log in.");
                window.location.href = 'login.html'; // Or wherever your login page is
            }
        } else {
            // This handles validation errors (e.g., "Username already taken")
            // If 'data' is a list of errors (Django style), you might need to format it
            const errorMsg = data.detail || JSON.stringify(data); 
            throw new Error(errorMsg);
        }
    } catch (error) {
        alert(error.message);
    }
}

export function logout() {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('username');
    window.location.href = 'index.html';
}

// Attach event listeners if on the login/signup page
const loginForm = document.getElementById('loginForm');
if (loginForm) {
    loginForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const u = document.getElementById('username').value;
        const p = document.getElementById('password').value;
        login(u, p);
    });
}

const signupForm = document.getElementById('signupForm');
if (signupForm) {
    signupForm.addEventListener('submit', (e) => {
        e.preventDefault();
        
        const u = document.getElementById('username').value;
        const em = document.getElementById('email').value;
        const p = document.getElementById('password').value;
        
        signup(u, em, p);
    });
}