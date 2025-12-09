# 🔮 Multi-Domain Intelligence Platform

A comprehensive, unified web application built with Python and Streamlit that serves **Cybersecurity Analysts**, **Data Scientists**, and **IT Administrators** with high-value analysis, insights, and operational capabilities.

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.29+-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Domain Dashboards](#domain-dashboards)
- [AI Integration](#ai-integration)
- [Technologies Used](#technologies-used)

## 🎯 Overview

This platform addresses three critical business problems:

| Domain | Problem Addressed | Key Insight |
|--------|------------------|-------------|
| **Cybersecurity** | Incident Response Bottleneck | Phishing surge identification & resolution time analysis |
| **Data Science** | Data Governance & Discovery | Dataset resource consumption & archiving recommendations |
| **IT Operations** | Service Desk Performance | Staff performance anomaly & process bottleneck identification |

## ✨ Features

### Core Features
- 🔐 **Secure Authentication** - bcrypt password hashing with role-based access
- 🗄️ **SQLite Database** - Full CRUD operations for all domains
- 📊 **Interactive Visualizations** - Plotly charts for data analysis
- 🤖 **AI Assistant** - Gemini-powered insights and recommendations
- 🎨 **Modern UI** - Beautiful dark theme with gradient accents

### Domain-Specific Features

#### 🛡️ Cybersecurity Dashboard
- Threat type distribution analysis
- Phishing surge detection and tracking
- Resolution time analysis by threat type
- Analyst workload and performance metrics
- Severity vs Status matrix visualization

#### 📊 Data Science Dashboard
- Storage consumption by department
- Dataset size distribution analysis
- Data quality scoring and tracking
- Archiving recommendations engine
- Data source dependency mapping

#### 🖥️ IT Operations Dashboard
- Staff performance comparison
- Process bottleneck identification
- SLA compliance monitoring
- Customer satisfaction analysis
- Ticket volume trending

## 🏗️ Architecture

### MVC Pattern Implementation
```
┌─────────────────────────────────────────────────────┐
│                    VIEW LAYER                        │
│  (Streamlit Pages: Login, Dashboards)               │
└─────────────────────┬───────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────┐
│                CONTROLLER LAYER                      │
│  (app.py - Session Management, Navigation)          │
└─────────────────────┬───────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────┐
│                  MODEL LAYER                         │
│  (database.py, models.py, auth.py)                  │
└─────────────────────┬───────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────┐
│                 DATA LAYER                           │
│  (SQLite Database, CSV Files)                       │
└─────────────────────────────────────────────────────┘
```

### Class Diagram (OOP Design)
```
┌──────────────────┐     ┌──────────────────┐
│      User        │     │  SecurityIncident │
├──────────────────┤     ├──────────────────┤
│ - user_id        │     │ - incident_id    │
│ - username       │     │ - title          │
│ - password_hash  │     │ - threat_type    │
│ - role           │     │ - severity       │
│ - created_at     │     │ - status         │
├──────────────────┤     ├──────────────────┤
│ + has_access_to()│     │ + is_phishing()  │
│ + to_dict()      │     │ + is_critical()  │
└──────────────────┘     │ + is_resolved()  │
                         └──────────────────┘

┌──────────────────┐     ┌──────────────────┐
│     Dataset      │     │     ITTicket     │
├──────────────────┤     ├──────────────────┤
│ - dataset_id     │     │ - ticket_id      │
│ - name           │     │ - title          │
│ - size_mb        │     │ - category       │
│ - quality_score  │     │ - priority       │
│ - status         │     │ - status         │
├──────────────────┤     ├──────────────────┤
│ + needs_archiving│     │ + is_resolved()  │
│ + is_large()     │     │ + get_age_hours()│
│ + get_size_cat() │     │ + is_waiting()   │
└──────────────────┘     └──────────────────┘
```

## 🚀 Installation

### Prerequisites
- Python 3.9 or higher
- pip (Python package installer)

### Step-by-Step Setup

1. **Clone or navigate to the project directory**
   ```bash
   cd project
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables for AI features**
   
   Create a `.env` file in the project root:
   ```
   GEMINI_API_KEY=your_gemini_api_key_here
   ```
   
   Get your Gemini API key from: https://aistudio.google.com/app/apikey

5. **Run the application**
   ```bash
   streamlit run app.py
   ```

6. **Access the application**
   
   Open your browser and navigate to: `http://localhost:8501`

## 📖 Usage

### First-Time Setup
1. Register a new account on the login page
2. Choose your role (admin has access to all dashboards)
3. Sample data is automatically loaded on first run

### Available Roles
- **admin** - Full access to all dashboards
- **cybersecurity** - Cybersecurity dashboard access
- **datascience** - Data Science dashboard access
- **it_operations** - IT Operations dashboard access

### Using the Dashboards
1. **Analytics Tab** - View visualizations and key insights
2. **Explorer Tab** - Search and filter through records
3. **Manage Tab** - Create, update, or delete records
4. **AI Assistant Tab** - Get AI-powered analysis and recommendations

## 📁 Project Structure

```
project/
├── app.py                 # Main Streamlit application
├── auth.py                # Authentication module (bcrypt hashing)
├── database.py            # SQLite database manager with CRUD
├── models.py              # OOP entity classes
├── ai_assistant.py        # Gemini AI integration
├── requirements.txt       # Python dependencies
├── README.md              # Project documentation
├── env_example.txt        # Environment variables template
├── users.txt              # File-based user storage (Week 7)
├── intelligence_platform.db  # SQLite database
├── data/
│   ├── cyber_incidents.csv     # Cybersecurity sample data
│   ├── datasets_metadata.csv   # Data Science sample data
│   └── it_tickets.csv          # IT Operations sample data
└── dashboards/
    ├── __init__.py
    ├── cybersecurity.py   # Cybersecurity dashboard
    ├── datascience.py     # Data Science dashboard
    └── it_operations.py   # IT Operations dashboard
```

## 🎨 Domain Dashboards

### 🛡️ Cybersecurity Dashboard

**Key Analysis:** Phishing Surge & Incident Response Bottleneck

The dashboard identifies:
- Rising phishing incidents as the dominant threat type
- Resolution time disparities across threat categories
- Analyst workload distribution and performance gaps
- Critical incidents requiring immediate attention

**Visualizations:**
- Threat type distribution (bar chart)
- Phishing incidents by status (pie chart)
- Daily incident timeline (area chart)
- Resolution time by severity/threat type (bar charts)
- Analyst performance comparison

### 📊 Data Science Dashboard

**Key Analysis:** Data Governance & Resource Consumption

The dashboard provides:
- Storage consumption analysis by department
- Dataset size distribution and categorization
- Data quality scoring across sources
- Archiving recommendations for stale/deprecated datasets

**Visualizations:**
- Storage by department (bar chart)
- Dataset distribution (pie chart)
- Size distribution histogram
- Quality vs Size scatter plot
- Data freshness analysis

### 🖥️ IT Operations Dashboard

**Key Analysis:** Staff Performance & Process Bottlenecks

The dashboard reveals:
- Performance anomalies between support staff
- "Waiting for User" as the primary bottleneck
- SLA compliance rates by priority
- Customer satisfaction metrics

**Visualizations:**
- Tickets by staff member (bar chart)
- Resolution time by staff (horizontal bar)
- Status distribution highlighting bottlenecks
- SLA compliance breakdown
- Satisfaction rating distribution

## 🤖 AI Integration

The platform integrates Google's Gemini AI with **domain-specific isolation**:

### Key Features
- **Separate API Keys** - Each domain uses its own Gemini API key
- **Data Isolation** - Each AI can only access its domain's database
- **Topic Restriction** - AI will refuse to answer off-topic questions
- **Automated Analysis** - One-click domain-specific analysis
- **Context-Aware Chat** - Ask questions about your specific domain data

### Security Architecture
| Domain | API Key Variable | Data Access | Allowed Topics |
|--------|-----------------|-------------|----------------|
| Cybersecurity | `GEMINI_API_KEY_CYBER` | Security incidents only | Threats, phishing, malware |
| Data Science | `GEMINI_API_KEY_DATA` | Dataset catalog only | Data governance, quality |
| IT Operations | `GEMINI_API_KEY_IT` | IT tickets only | Service desk, SLA, tickets |

### Setup
1. Get API keys from [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Create `.env` file with domain-specific keys:
   ```
   GEMINI_API_KEY_CYBER=your_cybersecurity_key
   GEMINI_API_KEY_DATA=your_datascience_key
   GEMINI_API_KEY_IT=your_it_operations_key
   ```
3. Restart the application

### Example Queries
- **Cybersecurity AI**: "What are the top security risks?" ✅ | "How many datasets exist?" ❌
- **Data Science AI**: "Which datasets need archiving?" ✅ | "Any phishing incidents?" ❌
- **IT Operations AI**: "Who has the longest resolution time?" ✅ | "Any malware detected?" ❌

## 🛠️ Technologies Used

| Technology | Purpose |
|------------|---------|
| **Python 3.9+** | Core programming language |
| **Streamlit** | Web application framework |
| **SQLite** | Database storage |
| **Pandas** | Data manipulation |
| **Plotly** | Interactive visualizations |
| **bcrypt** | Password hashing |
| **Google Generative AI** | Gemini AI integration |
| **python-dotenv** | Environment variable management |

## 📊 Database Schema

### Users Table
```sql
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL,
    created_at TEXT
);
```

### Cyber Incidents Table
```sql
CREATE TABLE cyber_incidents (
    incident_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    threat_type TEXT NOT NULL,
    severity TEXT NOT NULL,
    status TEXT NOT NULL,
    assigned_to TEXT,
    created_at TEXT NOT NULL,
    resolved_at TEXT,
    resolution_time_hours REAL,
    source_ip TEXT,
    target_system TEXT
);
```

### Datasets Metadata Table
```sql
CREATE TABLE datasets_metadata (
    dataset_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    source_department TEXT,
    file_format TEXT,
    size_mb REAL,
    row_count INTEGER,
    column_count INTEGER,
    uploaded_by TEXT,
    upload_date TEXT,
    last_accessed TEXT,
    quality_score REAL,
    status TEXT,
    storage_location TEXT
);
```

### IT Tickets Table
```sql
CREATE TABLE it_tickets (
    ticket_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    category TEXT NOT NULL,
    priority TEXT NOT NULL,
    status TEXT NOT NULL,
    requester TEXT,
    assigned_to TEXT,
    created_at TEXT NOT NULL,
    first_response_at TEXT,
    resolved_at TEXT,
    resolution_time_hours REAL,
    sla_met TEXT,
    department TEXT,
    satisfaction_rating INTEGER
);
```

## 📝 License

This project is created for educational purposes as part of CST1510 Coursework 2.

---

**Tier 3 Implementation** - Full implementation of all three domain dashboards with Authentication, Database, OOP, Visualizations, and AI Integration.

