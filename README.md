#  MailNexa – Intelligent Email Classification System

##  Overview

MailNexa is an intelligent email analysis system that integrates with Gmail, fetches recent emails, classifies them into meaningful categories, and assigns priority levels using a **Hybrid AI approach (Rule-Based + Machine Learning)**.

It helps users quickly identify important emails such as:

-  Deadlines  
-  Academic notifications  
-  Job alerts  
-  Security messages  

---

##  Key Features

-  Gmail integration using OAuth2  
-  Fetches recent emails (configurable time window – e.g., last 24 hours)  
-  Automatic email categorization  
-  Priority detection (**HIGH / MEDIUM / LOW**)  
-  Hybrid classification:
  - Rule-based logic  
  - Machine Learning fallback  
-  Explainable classification (shows reason for classification)  
-  Clean Chrome Extension inbox UI  

---

##  Email Categories

###  Education & Learning
- Academics (NPTEL, Coursera, Exams)
- Coding Platforms (LeetCode, GitHub)

###  Career & Work
- Jobs & Internships
- Interviews
- Meetings

###  Time-Sensitive
- Deadlines
- Finance / Transactions

###  Information & Content
- Newsletters
- Announcements

###  Other
- Promotions  
- Events  
- Social Notifications  
- Security Alerts  
- System Emails  
- Normal (fallback)  

---

## 🛠 Tech Stack

### Backend
- Python 3.11  
- FastAPI  
- Gmail API  

### Machine Learning
- Scikit-learn  
- TF-IDF Vectorizer  
- Logistic Regression  

### Frontend
- Chrome Extension (Manifest V3)  
- HTML, CSS, JavaScript  

---

##  Architecture Flow

Gmail API  
↓  
Email Fetcher  
↓  
Classification Pipeline  
↓  
Hybrid Classifier (Rule + ML)  
↓  
FastAPI Backend  
↓  
Chrome Extension UI  

---

##  Setup Instructions

### 1️ Enable Gmail API

1. Create a project in Google Cloud Console  
2. Enable Gmail API  
3. Download OAuth credentials  

Place the credentials file in:

---

### 2️ Generate Token (One-Time Setup)

```bash
cd backend
python auth_once.py
