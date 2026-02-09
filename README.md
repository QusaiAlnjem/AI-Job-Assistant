# 🚀 JobHunter AI

**JobHunter AI** is an intelligent "Reverse Recruiter" application designed to automate the job search process. It scans the web for relevant job listings, compares them against your resume using AI logic, and calculates a specific **Match Score** to help you focus on applications where you have the highest chance of success.

![Project Status](https://img.shields.io/badge/status-active-success.svg)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)
![Django](https://img.shields.io/badge/Django-4.2%2B-green.svg)
![Playwright](https://img.shields.io/badge/Playwright-Scraping-orange.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

---

## 🌟 Key Features

### 1. 📄 Smart Resume Parsing
* Upload your resume in **PDF** or **DOCX** format.
* The system automatically parses and extracts key skills to use for matching.

### 2. 🕵️‍♂️ Automated Job Scanner
* Powered by **Playwright**, the scanner searches job boards (e.g., *WeWorkRemotely*) in real-time.
* Filters jobs by **Remote**, **Hybrid**, or **On-Site** preferences.

### 3. 🧠 AI Match Engine
* Compares job descriptions against your resume profile.
* Generates a **0-100% Match Score**.
* Highlights **Missing Keywords** and provides actionable **Improvement Tips**.

### 4. ✅ Manual Job Check
* Found a job link elsewhere? Copy and paste the description into the **Job Check** tool.
* Get an instant analysis and match score without running a full scan.

### 5. 📊 Application Dashboard
* A Kanban-style dashboard to track your job hunt.
* Update statuses: `New` → `Applied` → `Interview` → `Offer`.
* Visual statistics for total applications and success rates.

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| **Backend** | Python, Django, Django REST Framework (DRF) |
| **Database** | SQLite (Dev) / PostgreSQL (Prod) |
| **Scraping** | Playwright (Headless Browser) |
| **Frontend** | HTML5, CSS3, Vanilla JavaScript (ES6 Modules) |
| **Auth** | Token-based Authentication |
