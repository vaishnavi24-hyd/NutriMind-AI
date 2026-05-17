# 🥗 NutriMind — AI Nutrition Intelligence Platform

<div align="center">

## 🚀 Multimodal AI-Powered Nutrition Analysis System

### Built with Local LLMs, Computer Vision, OCR & Advanced Analytics

</div>

---

# 📌 Project Overview

NutriMind is a futuristic AI-powered nutrition intelligence platform that uses multimodal AI models to analyze food images, estimate nutritional values, generate health insights, and track user dietary habits through an advanced analytics dashboard.

The application combines:

* 🧠 Local LLMs with Ollama
* 👁️ Vision-based food understanding
* 📊 Interactive nutrition analytics
* 🏷️ OCR-powered food label scanning
* 💾 Persistent meal tracking with SQLite
* 🌌 Premium neon cyberpunk UI

Unlike traditional calorie tracker apps, NutriMind uses AI to understand meals directly from uploaded images and provide intelligent health feedback.

---

# ✨ Key Features

## 🍔 AI Meal Analysis

* Upload meal images
* AI detects food items
* Nutrition estimation:

  * Calories
  * Protein
  * Carbs
  * Fat
* Health score generation
* AI-generated nutrition summary
* Personalized recommendations

---

## 🧠 Local Multimodal AI

Powered completely using:

* Ollama
* llama3.2-vision

The system runs locally on the machine without requiring cloud AI APIs.

---

## 📊 Advanced Analytics Dashboard

Interactive analytics system featuring:

* Daily calorie trends
* Protein tracking
* Meal frequency insights
* Average health score monitoring
* Nutrition overview cards
* Interactive data visualization

---

## 🏷️ OCR Food Label Scanner

AI-powered packaged food analysis:

* OCR ingredient extraction
* Nutrition label scanning
* Preservative detection
* Ultra-processed food warnings
* Health impact analysis
* Ingredient explanations

---

## 🌌 Premium Futuristic UI

Custom-designed neon cyberpunk interface:

* Glassmorphism design
* Neon glow effects
* Dark futuristic theme
* Responsive layouts
* Animated components
* Premium dashboard styling

---

## 💾 Meal Tracking & Persistence

* SQLite database integration
* Meal history tracking
* Nutrition persistence
* Analytics-ready architecture
* User-specific meal storage foundation

---

# 🧱 System Architecture

```text
User Uploads Meal Image
            ↓
     Streamlit Frontend
            ↓
   Image Processing Layer
            ↓
       Ollama Engine
            ↓
     llama3.2-vision
            ↓
 Structured Nutrition JSON
            ↓
 SQLite Database Storage
            ↓
 Analytics Dashboard
```

---

# 🛠️ Tech Stack

## Frontend

* Streamlit
* Custom CSS
* Plotly

---

## AI & Machine Learning

* Ollama
* llama3.2-vision
* Mistral
* OCR Processing

---

## Backend & Database

* Python
* SQLite
* SQLAlchemy

---

## Data Processing

* Pandas
* NumPy
* Pillow

---

## OCR & Image Processing

* pytesseract
* OpenCV
* PIL

---

# 📂 Project Structure

```text
food_analyzer/
│
├── app.py
├── services/
│   ├── ai_service.py
│   ├── auth_service.py
│   ├── ocr_service.py
│   └── analytics_service.py
│
├── components/
│   ├── dashboard.py
│   ├── analytics.py
│   ├── upload_meal.py
│   └── sidebar.py
│
├── database/
│   ├── models/
│   └── database.py
│
├── uploads/
├── assets/
├── screenshots/
├── requirements.txt
└── README.md
```

---

# ⚙️ Installation Guide

## 1️⃣ Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/nutrimind.git
cd nutrimind
```

---

## 2️⃣ Create Virtual Environment

### Mac/Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

### Windows

```bash
python -m venv venv
venv\\Scripts\\activate
```

---

## 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

# 🤖 Ollama Setup

## Install Ollama

Download from:

[https://ollama.com](https://ollama.com)

---

## Start Ollama

```bash
ollama serve
```

---

## Pull Vision Model

```bash
ollama pull llama3.2-vision
```

---

## Verify Installation

```bash
ollama list
```

Expected Output:

```bash
llama3.2-vision:latest
```

---

# ▶️ Run The Application

```bash
streamlit run app.py
```

Open:

```text
http://localhost:8501
```

---




# 🎯 Current Features Completed

✅ AI meal image analysis

✅ Local multimodal AI using Ollama

✅ Nutrition estimation engine

✅ Health scoring system

✅ AI nutrition recommendations

✅ OCR food label scanner

✅ Analytics dashboard

✅ SQLite persistence

✅ Premium futuristic UI

✅ Responsive dashboard architecture

---



---

# 💡 Challenges Solved

This project involved solving:

* Structured AI response parsing
* Local multimodal inference pipelines
* OCR integration workflows
* Real-time nutrition estimation
* Streamlit UI engineering
* Neon cyberpunk dashboard design
* SQLite analytics persistence
* Ollama local model integration

---

# 📈 Learning Outcomes

Through this project, key skills developed include:

* Multimodal AI engineering
* Local LLM deployment
* Vision model integration
* Prompt engineering
* OCR systems
* Database architecture
* Dashboard analytics
* Advanced Streamlit UI design
* AI workflow orchestration

---

# 🔥 Why This Project Stands Out

NutriMind combines multiple modern AI engineering concepts into one cohesive product:

* Computer Vision
* Local LLMs
* OCR
* AI Analytics
* Health Intelligence
* Interactive Dashboards
* SaaS-style architecture

This makes it significantly more advanced than standard CRUD or API-based student projects.

---

# 🤝 Contributing

Contributions, suggestions, and improvements are welcome.

Feel free to fork the repository and submit pull requests.

---

# 📜 License

This project is licensed under the MIT License.

---

