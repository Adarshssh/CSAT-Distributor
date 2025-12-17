# CSAT-Chat-Automation

## 📌 Project Overview
**CSAT-Chat-Automation** is a Python-based automation learning project built using **Playwright**.
This project simulates customer support live chat workflows and submits CSAT (Customer Satisfaction)
feedback after chat resolution.

The project focuses on demonstrating **browser automation**, **workflow handling**, and
**multi-scenario execution** using Playwright.

---

## 🎯 Purpose
This project is created **strictly for educational and automation learning purposes**.

It demonstrates:
- Automated login flows
- Live chat initiation and category selection
- Human-like chat interactions
- Scenario-based automation
- Automated CSAT feedback submission

---

## 🧠 Key Features
- Automated login using multiple email accounts
- Common password handling for all accounts
- Live chat automation with realistic delays
- Multiple support category workflows
- Automated chat termination and CSAT feedback
- Parallel execution for POCO support scenarios
- Modular script-based design

---

## 📂 Supported Support Categories
The project includes separate scripts for different support flows:

- 📱 Smartphone Support
- 💻 Laptop Support
- ⭐ Premium Support
- 🗣️ Hindi Language Support
- 📦 POCO Support (Single Instance)
- ⚡ POCO Support (4 Parallel Instances using same browser type)

---

## 🏗️ Project Structure
```
CSAT-Chat-Automation/
│
├── scripts/
│   ├── csat_core_engine.py
│   ├── csat_smartphone_support.py
│   ├── csat_laptop_support.py
│   ├── csat_premium_support.py
│   ├── csat_hindi_support.py
│   ├── csat_poco_support.py
│   ├── csat_poco_parallel_support.py
│   └── emails.txt
│
├── requirements.txt
├── README.md
└── .gitignore
```

---

## 🔐 Authentication Details
- `emails.txt` is placed inside the `scripts/` folder
- It contains all email IDs used for login
- A **single common password** is used for all accounts
- Password is stored directly inside the scripts for learning purposes

⚠️ **Note:** Credentials should never be committed in real-world production systems.

---

## 🛠️ Tech Stack
- **Language:** Python 3.x
- **Automation Tool:** Playwright (Sync API)
- **Browser:** Chromium (Playwright-managed)

---

## 📦 Installation & Setup

### 1️⃣ Clone the repository
```bash
git clone https://github.com/<your-github-username>/CSAT-Chat-Automation.git
cd CSAT-Chat-Automation
```

### 2️⃣ Install dependencies
```bash
pip install -r requirements.txt
```

### 3️⃣ Install Playwright browsers
```bash
playwright install
```

---

## ▶️ Running the Scripts

Run any script from the `scripts` directory:

```bash
python scripts/csat_smartphone_support.py
```

For POCO parallel execution:

```bash
python scripts/csat_poco_parallel_support.py
```

---

## ⚠️ Disclaimer
> **This project is for educational and automation learning purposes only.**
> It is not intended for misuse, abuse, or violation of any platform’s terms of service.

---

## 👤 Author
**GitHub:** <your-github-username>

---

## 🚀 Learning Outcomes
This project demonstrates:
- End-to-end browser automation
- Real-time interaction handling
- Scenario-based scripting
- Parallel execution concepts
- Professional automation project structuring
