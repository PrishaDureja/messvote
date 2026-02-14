# MessVote

## AI-Assisted Hostel Mess Feedback and Analytics System

---

## Overview

MessVote is a web-based hostel mess feedback and analytics system that collects, processes, and interprets student opinions using Natural Language Processing (NLP) and machine learning.

Traditional feedback systems store ratings and comments without structured analysis. MessVote transforms raw feedback into actionable insights by combining sentiment analysis, aspect classification, and dashboard visualization.

The system enables data-driven decision-making for mess administrators.

---

## Problem Statement

Hostel mess management typically relies on manual review of ratings and written comments. This approach is inefficient and makes it difficult to detect recurring complaints or sentiment trends over time.

There is a need for a structured solution that:

- Collects feedback systematically  
- Analyzes textual complaints automatically  
- Identifies recurring problem areas  
- Supports data-backed administrative decisions  

MessVote is designed to address this gap.

---

## Core Features

### Student Module

- Mess selection and login system  
- Meal-wise rating submission (Breakfast, Lunch, Dinner)  
- 1–5 star rating mechanism  
- Textual feedback submission  
- Session-based authentication  

### Admin Module

- Secure admin login  
- Menu management interface  
- Real-time dashboard  
- Dish-wise rating analysis  
- Weekly performance tracking  
- Complaint and suggestion monitoring  

---

## NLP and Machine Learning Components

MessVote integrates multiple NLP techniques to process and structure feedback data.

### 1. VADER Sentiment Analysis

- Rule-based sentiment scoring  
- Optimized for short informal text  
- Classifies feedback as Positive, Neutral, or Negative  

### 2. TF-IDF Vectorization

- Converts text into numerical feature vectors  
- Reduces noise from frequent common words  
- Improves classification accuracy  

### 3. Multinomial Naive Bayes Classifier

- Supervised learning model  
- Trained on labeled feedback data  
- Used for sentiment prediction  

### 4. Aspect-Based Classification

Feedback is categorized into structured aspects such as:

- Food Quality  
- Hygiene  
- Service  

This enables administrators to detect recurring issue patterns instead of manually reviewing comments.

---

## Analytics Capabilities

- Dish-wise average rating computation  
- Meal-wise performance comparison  
- Weekly trend visualization  
- Sentiment distribution analysis  
- Complaint percentage by aspect  

These features convert unstructured feedback into measurable insights.

---

## Technology Stack

### Backend
- Python  
- Flask  
- SQLAlchemy  

### Frontend
- HTML  
- CSS  
- JavaScript  

### Database
- SQLite (Development)  
- PostgreSQL (Production-ready)  

### Machine Learning
- Scikit-learn  
- NLTK (VADER)  
- TF-IDF  
- Multinomial Naive Bayes  

### Deployment
- Render (Application Hosting)  
- GitHub (Version Control)  
- GitHub Pages (Presentation Hosting)  

---

## System Workflow

1. Student submits rating and feedback  
2. Text is cleaned and normalized  
3. TF-IDF transforms text into feature vectors  
4. Sentiment is predicted using Naive Bayes and VADER  
5. Aspect classification categorizes the complaint  
6. Data is stored in the database  
7. Admin dashboard visualizes structured analytics  

---

## Live Links

Application:  
https://messvote.onrender.com  

Presentation:  
https://prishadureja.github.io/pbl_project/

---

## Project Status

Version 1: Stable feedback collection and analytics dashboard  

Version 2: Integrated NLP-based sentiment and aspect classification  

The system is under continuous development with a focus on scalability and structured intelligence.
