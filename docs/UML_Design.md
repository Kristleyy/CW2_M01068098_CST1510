# UML Design - Multi-Domain Intelligence Platform

## 1. Class Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              MULTI-DOMAIN INTELLIGENCE PLATFORM                      │
│                                    CLASS DIAGRAM                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────┐          ┌──────────────────────────────┐
│          <<dataclass>>       │          │        AuthManager           │
│            User              │          ├──────────────────────────────┤
├──────────────────────────────┤          │ - users_file: str            │
│ - user_id: int               │          ├──────────────────────────────┤
│ - username: str              │          │ + __init__(users_file)       │
│ - password_hash: str         │          │ + hash_password(password)    │
│ - role: str                  │          │ + verify_password(pwd, hash) │
│ - created_at: datetime       │          │ + register_user(user, pwd)   │
├──────────────────────────────┤          │ + login(username, password)  │
│ + has_access_to(domain): bool│          │ + get_user(username)         │
│ + to_dict(): dict            │          │ + get_all_users()            │
└──────────────────────────────┘          └──────────────────────────────┘
              │                                         │
              │ authenticates                           │
              └──────────────────┬──────────────────────┘
                                 │
                                 ▼
┌──────────────────────────────────────────────────────────────────────────────────────┐
│                                  DatabaseManager                                      │
├──────────────────────────────────────────────────────────────────────────────────────┤
│ - db_path: str                                                                       │
├──────────────────────────────────────────────────────────────────────────────────────┤
│ + __init__(db_path)                                                                  │
│ + get_connection()                                                                   │
│ + _init_database()                                                                   │
│ ─────────────────────────────── USER CRUD ───────────────────────────────────────── │
│ + create_user(username, password_hash, role): bool                                   │
│ + get_user(username): tuple                                                          │
│ + get_all_users(): list                                                              │
│ + update_user(username, **kwargs): bool                                              │
│ + delete_user(username): bool                                                        │
│ ─────────────────────────────── INCIDENT CRUD ───────────────────────────────────── │
│ + create_incident(incident_data): bool                                               │
│ + get_incident(incident_id): tuple                                                   │
│ + get_all_incidents(): list                                                          │
│ + get_incidents_dataframe(): DataFrame                                               │
│ + update_incident(incident_id, **kwargs): bool                                       │
│ + delete_incident(incident_id): bool                                                 │
│ ─────────────────────────────── DATASET CRUD ────────────────────────────────────── │
│ + create_dataset(dataset_data): bool                                                 │
│ + get_dataset(dataset_id): tuple                                                     │
│ + get_all_datasets(): list                                                           │
│ + get_datasets_dataframe(): DataFrame                                                │
│ + update_dataset(dataset_id, **kwargs): bool                                         │
│ + delete_dataset(dataset_id): bool                                                   │
│ ─────────────────────────────── TICKET CRUD ─────────────────────────────────────── │
│ + create_ticket(ticket_data): bool                                                   │
│ + get_ticket(ticket_id): tuple                                                       │
│ + get_all_tickets(): list                                                            │
│ + get_tickets_dataframe(): DataFrame                                                 │
│ + update_ticket(ticket_id, **kwargs): bool                                           │
│ + delete_ticket(ticket_id): bool                                                     │
│ ─────────────────────────────── ANALYTICS ───────────────────────────────────────── │
│ + get_incident_stats(): dict                                                         │
│ + get_dataset_stats(): dict                                                          │
│ + get_ticket_stats(): dict                                                           │
│ + load_all_sample_data(data_dir): dict                                               │
└──────────────────────────────────────────────────────────────────────────────────────┘
                                         │
            ┌────────────────────────────┼────────────────────────────┐
            │                            │                            │
            ▼                            ▼                            ▼
┌─────────────────────────┐  ┌─────────────────────────┐  ┌─────────────────────────┐
│    <<dataclass>>        │  │    <<dataclass>>        │  │    <<dataclass>>        │
│   SecurityIncident      │  │       Dataset           │  │       ITTicket          │
├─────────────────────────┤  ├─────────────────────────┤  ├─────────────────────────┤
│ - incident_id: str      │  │ - dataset_id: str       │  │ - ticket_id: str        │
│ - title: str            │  │ - name: str             │  │ - title: str            │
│ - description: str      │  │ - description: str      │  │ - description: str      │
│ - threat_type: str      │  │ - source_department: str│  │ - category: str         │
│ - severity: str         │  │ - file_format: str      │  │ - priority: str         │
│ - status: str           │  │ - size_mb: float        │  │ - status: str           │
│ - assigned_to: str      │  │ - row_count: int        │  │ - requester: str        │
│ - created_at: datetime  │  │ - column_count: int     │  │ - assigned_to: str      │
│ - resolved_at: datetime │  │ - uploaded_by: str      │  │ - created_at: datetime  │
│ - resolution_time: float│  │ - upload_date: datetime │  │ - first_response: dt    │
│ - source_ip: str        │  │ - last_accessed: dt     │  │ - resolved_at: datetime │
│ - target_system: str    │  │ - quality_score: float  │  │ - resolution_time: float│
├─────────────────────────┤  │ - status: str           │  │ - sla_met: bool         │
│ + is_phishing(): bool   │  │ - storage_location: str │  │ - department: str       │
│ + is_critical(): bool   │  ├─────────────────────────┤  │ - satisfaction: int     │
│ + is_resolved(): bool   │  │ + needs_archiving(): bool│ ├─────────────────────────┤
│ + get_backlog_age(): hr │  │ + is_large_dataset(): bl│  │ + is_waiting(): bool    │
│ + to_dict(): dict       │  │ + get_size_category(): s│  │ + is_resolved(): bool   │
└─────────────────────────┘  │ + to_dict(): dict       │  │ + get_response_time(): h│
                             └─────────────────────────┘  │ + get_age_hours(): float│
                                                          │ + to_dict(): dict       │
                                                          └─────────────────────────┘
```

---

## 2. Use Case Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              USE CASE DIAGRAM                                        │
└─────────────────────────────────────────────────────────────────────────────────────┘

    ┌─────────┐                                                    ┌─────────┐
    │  Admin  │                                                    │  Guest  │
    └────┬────┘                                                    └────┬────┘
         │                                                              │
         │  ┌──────────────────────────────────────────────────────┐   │
         │  │                    SYSTEM                             │   │
         │  │                                                       │   │
         ├──┼──►  ○ Access All Dashboards                          │   │
         │  │                                                       │   │
         │  │     ○ Manage Users                                    │   │
         │  │                                                       │   │
         │  │  ┌─────────────────────────────────────────────────┐ │   │
         │  │  │           AUTHENTICATION                         │ │   │
         │  │  │                                                  │ │   │
         │  │  │    ○ Register Account ◄────────────────────────┼─┼───┤
         │  │  │                                                  │ │   │
         │  │  │    ○ Login ◄───────────────────────────────────┼─┼───┤
         │  │  │                                                  │ │
         │  │  │    ○ Logout                                      │ │
         │  │  │                                                  │ │
         │  │  └─────────────────────────────────────────────────┘ │
         │  └──────────────────────────────────────────────────────┘
         │
    ┌────┴────────────────────────────────────────────────────────────────┐
    │                                                                      │
    │                                                                      │
┌───┴───┐              ┌───────────┐                    ┌─────────────┐   │
│Cyber  │              │   Data    │                    │     IT      │   │
│Analyst│              │ Scientist │                    │Administrator│   │
└───┬───┘              └─────┬─────┘                    └──────┬──────┘   │
    │                        │                                  │          │
    │  ┌─────────────────────┼──────────────────────────────────┼──────┐  │
    │  │  CYBERSECURITY      │                                  │      │  │
    │  │  DASHBOARD          │                                  │      │  │
    │  │                     │                                  │      │  │
    ├──┼──► ○ View Incidents │                                  │      │  │
    │  │                     │                                  │      │  │
    ├──┼──► ○ Analyze Threats│                                  │      │  │
    │  │                     │                                  │      │  │
    ├──┼──► ○ Manage CRUD    │                                  │      │  │
    │  │      (Create/Update/│                                  │      │  │
    │  │       Delete)       │                                  │      │  │
    ├──┼──► ○ Chat with AI   │                                  │      │  │
    │  │      Security       │                                  │      │  │
    │  │      Analyst        │                                  │      │  │
    │  └─────────────────────┼──────────────────────────────────┼──────┘  │
    │                        │                                  │          │
    │  ┌─────────────────────┼──────────────────────────────────┼──────┐  │
    │  │  DATA SCIENCE       │                                  │      │  │
    │  │  DASHBOARD          │                                  │      │  │
    │  │                     │                                  │      │  │
    │  │                     ├──► ○ View Datasets               │      │  │
    │  │                     │                                  │      │  │
    │  │                     ├──► ○ Analyze Data Quality        │      │  │
    │  │                     │                                  │      │  │
    │  │                     ├──► ○ Manage CRUD                 │      │  │
    │  │                     │      (Register/Update/Delete)    │      │  │
    │  │                     │                                  │      │  │
    │  │                     ├──► ○ Chat with AI                │      │  │
    │  │                     │      Data Advisor                │      │  │
    │  └─────────────────────┼──────────────────────────────────┼──────┘  │
    │                        │                                  │          │
    │  ┌─────────────────────┼──────────────────────────────────┼──────┐  │
    │  │  IT OPERATIONS      │                                  │      │  │
    │  │  DASHBOARD          │                                  │      │  │
    │  │                     │                                  │      │  │
    │  │                     │                                  ├──► ○ View Tickets
    │  │                     │                                  │      │  │
    │  │                     │                                  ├──► ○ Analyze SLA
    │  │                     │                                  │      │  │
    │  │                     │                                  ├──► ○ Manage CRUD
    │  │                     │                                  │      (Create/Update/Delete)
    │  │                     │                                  │      │  │
    │  │                     │                                  ├──► ○ Chat with AI
    │  │                     │                                  │      IT Advisor
    │  └─────────────────────┼──────────────────────────────────┼──────┘  │
    │                        │                                  │          │
    └────────────────────────┴──────────────────────────────────┴──────────┘
```

---

## 3. Sequence Diagram - Login Flow

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                         SEQUENCE DIAGRAM - LOGIN FLOW                                │
└─────────────────────────────────────────────────────────────────────────────────────┘

    ┌──────┐          ┌────────┐         ┌─────────────┐      ┌────────────────┐
    │ User │          │ app.py │         │ AuthManager │      │ DatabaseManager│
    └──┬───┘          └───┬────┘         └──────┬──────┘      └───────┬────────┘
       │                  │                     │                     │
       │  1. Enter        │                     │                     │
       │  credentials     │                     │                     │
       │─────────────────►│                     │                     │
       │                  │                     │                     │
       │                  │  2. get_user()      │                     │
       │                  │────────────────────────────────────────────►
       │                  │                     │                     │
       │                  │  3. Return user     │                     │
       │                  │◄────────────────────────────────────────────
       │                  │                     │                     │
       │                  │  4. verify_password │                     │
       │                  │────────────────────►│                     │
       │                  │                     │                     │
       │                  │  5. Return bool     │                     │
       │                  │◄────────────────────│                     │
       │                  │                     │                     │
       │                  │  6. Set session_state                     │
       │                  │     authenticated=True                    │
       │                  │     user={username, role}                 │
       │                  │                     │                     │
       │  7. Show         │                     │                     │
       │  "Logged in"     │                     │                     │
       │◄─────────────────│                     │                     │
       │                  │                     │                     │
       │  8. Click        │                     │                     │
       │  dashboard link  │                     │                     │
       │─────────────────►│                     │                     │
       │                  │                     │                     │
    ┌──┴───┐          ┌───┴────┐         ┌──────┴──────┐      ┌───────┴────────┐
    │ User │          │ app.py │         │ AuthManager │      │ DatabaseManager│
    └──────┘          └────────┘         └─────────────┘      └────────────────┘
```

---

## 4. Sequence Diagram - Dashboard Access

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                    SEQUENCE DIAGRAM - DASHBOARD ACCESS                               │
└─────────────────────────────────────────────────────────────────────────────────────┘

    ┌──────┐       ┌───────────────┐    ┌────────────────┐    ┌─────────────┐
    │ User │       │ cybersecurity │    │ DatabaseManager│    │ AI Assistant│
    └──┬───┘       │    .py        │    └───────┬────────┘    └──────┬──────┘
       │           └───────┬───────┘            │                    │
       │                   │                    │                    │
       │  1. Navigate to   │                    │                    │
       │  /cybersecurity   │                    │                    │
       │──────────────────►│                    │                    │
       │                   │                    │                    │
       │                   │ 2. check_          │                    │
       │                   │ authentication()   │                    │
       │                   │ (session_state)    │                    │
       │                   │                    │                    │
       │                   │ 3. init_           │                    │
       │                   │ session_state()    │                    │
       │                   │───────────────────►│                    │
       │                   │                    │                    │
       │                   │ 4. get_incidents_  │                    │
       │                   │ dataframe()        │                    │
       │                   │───────────────────►│                    │
       │                   │                    │                    │
       │                   │ 5. Return DataFrame│                    │
       │                   │◄───────────────────│                    │
       │                   │                    │                    │
       │                   │ 6. get_incident_   │                    │
       │                   │ stats()            │                    │
       │                   │───────────────────►│                    │
       │                   │                    │                    │
       │                   │ 7. Return stats    │                    │
       │                   │◄───────────────────│                    │
       │                   │                    │                    │
       │ 8. Display        │                    │                    │
       │ Dashboard         │                    │                    │
       │◄──────────────────│                    │                    │
       │                   │                    │                    │
       │ 9. Ask AI         │                    │                    │
       │ question          │                    │                    │
       │──────────────────►│                    │                    │
       │                   │                    │                    │
       │                   │ 10. chat(prompt,db)│                    │
       │                   │────────────────────────────────────────►│
       │                   │                    │                    │
       │                   │ 11. Return response│                    │
       │                   │◄────────────────────────────────────────│
       │                   │                    │                    │
       │ 12. Display       │                    │                    │
       │ AI response       │                    │                    │
       │◄──────────────────│                    │                    │
       │                   │                    │                    │
    ┌──┴───┐       ┌───────┴───────┐    ┌───────┴────────┐    ┌──────┴──────┐
    │ User │       │ cybersecurity │    │ DatabaseManager│    │ AI Assistant│
    └──────┘       │    .py        │    └────────────────┘    └─────────────┘
                   └───────────────┘
```

---

## 5. Component Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              COMPONENT DIAGRAM                                       │
└─────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              PRESENTATION LAYER                                      │
│  ┌─────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐    │
│  │   app.py    │  │  cybersecurity  │  │   datascience   │  │  it_operations  │    │
│  │   (Login)   │  │     .py         │  │      .py        │  │      .py        │    │
│  │             │  │                 │  │                 │  │                 │    │
│  │ • Login Form│  │ • Analytics Tab │  │ • Analytics Tab │  │ • Analytics Tab │    │
│  │ • Register  │  │ • Explorer Tab  │  │ • Explorer Tab  │  │ • Explorer Tab  │    │
│  │ • Redirect  │  │ • CRUD Tab      │  │ • CRUD Tab      │  │ • CRUD Tab      │    │
│  │             │  │ • AI Chat Tab   │  │ • AI Chat Tab   │  │ • AI Chat Tab   │    │
│  └──────┬──────┘  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘    │
│         │                  │                    │                    │              │
└─────────┼──────────────────┼────────────────────┼────────────────────┼──────────────┘
          │                  │                    │                    │
          ▼                  ▼                    ▼                    ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              BUSINESS LOGIC LAYER                                    │
│                                                                                      │
│  ┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐     │
│  │     AuthManager     │    │   DatabaseManager   │    │    AI Assistant     │     │
│  │      (auth.py)      │    │   (database.py)     │    │  (ai_assistant.py)  │     │
│  │                     │    │                     │    │                     │     │
│  │ • Password Hashing  │    │ • CRUD Operations   │    │ • Domain-specific   │     │
│  │ • Login/Logout      │    │ • Data Analytics    │    │   AI Chat           │     │
│  │ • User Registration │    │ • Statistics        │    │ • Data Analysis     │     │
│  └──────────┬──────────┘    └──────────┬──────────┘    └──────────┬──────────┘     │
│             │                          │                          │                 │
└─────────────┼──────────────────────────┼──────────────────────────┼─────────────────┘
              │                          │                          │
              ▼                          ▼                          ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                                DATA LAYER                                            │
│                                                                                      │
│  ┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐     │
│  │     models.py       │    │    SQLite DB        │    │    CSV Files        │     │
│  │                     │    │                     │    │                     │     │
│  │ • User              │    │ • users             │    │ • cyber_incidents   │     │
│  │ • SecurityIncident  │    │ • cyber_incidents   │    │ • datasets_metadata │     │
│  │ • Dataset           │    │ • datasets_metadata │    │ • it_tickets        │     │
│  │ • ITTicket          │    │ • it_tickets        │    │                     │     │
│  │                     │    │                     │    │                     │     │
│  └─────────────────────┘    └─────────────────────┘    └─────────────────────┘     │
│                                                                                      │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 6. Entity Relationship Diagram (ERD)

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                        ENTITY RELATIONSHIP DIAGRAM                                   │
└─────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────┐
│           USERS             │
├─────────────────────────────┤
│ PK  user_id        INTEGER  │
│     username       TEXT     │─────────────────────────────────────────┐
│     password_hash  TEXT     │                                         │
│     role           TEXT     │                                         │
│     created_at     TEXT     │                                         │
└─────────────────────────────┘                                         │
                                                                        │
         ┌──────────────────────────────────────────────────────────────┘
         │  assigned_to / uploaded_by / requester
         ▼
┌─────────────────────────────┐  ┌─────────────────────────────┐  ┌─────────────────────────────┐
│     CYBER_INCIDENTS         │  │     DATASETS_METADATA       │  │        IT_TICKETS           │
├─────────────────────────────┤  ├─────────────────────────────┤  ├─────────────────────────────┤
│ PK  incident_id    TEXT     │  │ PK  dataset_id     TEXT     │  │ PK  ticket_id      TEXT     │
│     title          TEXT     │  │     name           TEXT     │  │     title          TEXT     │
│     description    TEXT     │  │     description    TEXT     │  │     description    TEXT     │
│     threat_type    TEXT     │  │     source_dept    TEXT     │  │     category       TEXT     │
│     severity       TEXT     │  │     file_format    TEXT     │  │     priority       TEXT     │
│     status         TEXT     │  │     size_mb        REAL     │  │     status         TEXT     │
│ FK  assigned_to    TEXT     │  │     row_count      INTEGER  │  │ FK  requester      TEXT     │
│     created_at     TEXT     │  │     column_count   INTEGER  │  │ FK  assigned_to    TEXT     │
│     resolved_at    TEXT     │  │ FK  uploaded_by    TEXT     │  │     created_at     TEXT     │
│     resolution_hrs REAL     │  │     upload_date    TEXT     │  │     first_response TEXT     │
│     source_ip      TEXT     │  │     last_accessed  TEXT     │  │     resolved_at    TEXT     │
│     target_system  TEXT     │  │     quality_score  REAL     │  │     resolution_hrs REAL     │
└─────────────────────────────┘  │     status         TEXT     │  │     sla_met        TEXT     │
                                 │     storage_loc    TEXT     │  │     department     TEXT     │
                                 └─────────────────────────────┘  │     satisfaction   INTEGER  │
                                                                  └─────────────────────────────┘
```

---

## 7. State Diagram - User Session

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                         STATE DIAGRAM - USER SESSION                                 │
└─────────────────────────────────────────────────────────────────────────────────────┘

                              ┌─────────────┐
                              │   START     │
                              └──────┬──────┘
                                     │
                                     ▼
                    ┌────────────────────────────────┐
                    │                                │
                    │      UNAUTHENTICATED           │
                    │      (Login Page)              │
                    │                                │
                    └────────────────┬───────────────┘
                                     │
                         Login Success│
                                     │
                                     ▼
                    ┌────────────────────────────────┐
                    │                                │
                    │       AUTHENTICATED            │
                    │    (Logged In Page)            │
                    │                                │
                    └─────────┬──────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              │               │               │
              ▼               ▼               ▼
    ┌─────────────────┐ ┌─────────────┐ ┌─────────────────┐
    │  CYBERSECURITY  │ │ DATASCIENCE │ │  IT_OPERATIONS  │
    │    DASHBOARD    │ │  DASHBOARD  │ │    DASHBOARD    │
    │                 │ │             │ │                 │
    │ • View Analytics│ │ • View Data │ │ • View Tickets  │
    │ • Explore       │ │ • Explore   │ │ • Explore       │
    │ • CRUD          │ │ • CRUD      │ │ • CRUD          │
    │ • AI Chat       │ │ • AI Chat   │ │ • AI Chat       │
    └────────┬────────┘ └──────┬──────┘ └────────┬────────┘
             │                 │                 │
             │    Logout       │    Logout       │    Logout
             │                 │                 │
             └─────────────────┼─────────────────┘
                               │
                               ▼
                    ┌────────────────────────────────┐
                    │                                │
                    │      UNAUTHENTICATED           │
                    │      (Login Page)              │
                    │                                │
                    └────────────────────────────────┘
```

---

## 8. Activity Diagram - CRUD Operations

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                    ACTIVITY DIAGRAM - CRUD OPERATIONS                                │
└─────────────────────────────────────────────────────────────────────────────────────┘

                              ┌─────────────┐
                              │   START     │
                              └──────┬──────┘
                                     │
                                     ▼
                         ┌───────────────────────┐
                         │  Select CRUD Action   │
                         └───────────┬───────────┘
                                     │
              ┌──────────────────────┼──────────────────────┐
              │                      │                      │
              ▼                      ▼                      ▼
     ┌────────────────┐     ┌────────────────┐     ┌────────────────┐
     │    CREATE      │     │    UPDATE      │     │    DELETE      │
     └───────┬────────┘     └───────┬────────┘     └───────┬────────┘
             │                      │                      │
             ▼                      ▼                      ▼
     ┌────────────────┐     ┌────────────────┐     ┌────────────────┐
     │  Fill Form     │     │ Select Record  │     │ Select Record  │
     │  with Details  │     │   to Update    │     │   to Delete    │
     └───────┬────────┘     └───────┬────────┘     └───────┬────────┘
             │                      │                      │
             ▼                      ▼                      ▼
     ┌────────────────┐     ┌────────────────┐     ┌────────────────┐
     │   Validate     │     │  Modify Fields │     │    Confirm     │
     │   Input Data   │     │                │     │    Deletion    │
     └───────┬────────┘     └───────┬────────┘     └───────┬────────┘
             │                      │                      │
             ▼                      ▼                      ▼
     ┌────────────────┐     ┌────────────────┐     ┌────────────────┐
     │  Save to DB    │     │  Update in DB  │     │ Delete from DB │
     │                │     │                │     │                │
     └───────┬────────┘     └───────┬────────┘     └───────┬────────┘
             │                      │                      │
             └──────────────────────┼──────────────────────┘
                                    │
                                    ▼
                         ┌───────────────────────┐
                         │   Display Success/    │
                         │   Error Message       │
                         └───────────┬───────────┘
                                     │
                                     ▼
                         ┌───────────────────────┐
                         │    Refresh Data       │
                         │      Display          │
                         └───────────┬───────────┘
                                     │
                                     ▼
                              ┌─────────────┐
                              │    END      │
                              └─────────────┘
```

---

## Summary

This UML design documents the **Multi-Domain Intelligence Platform** architecture:

| Diagram | Purpose |
|---------|---------|
| Class Diagram | Shows all classes and their relationships |
| Use Case Diagram | Shows what each user role can do |
| Sequence Diagrams | Shows the flow of login and dashboard access |
| Component Diagram | Shows the 3-layer architecture |
| ERD | Shows database table relationships |
| State Diagram | Shows user session states |
| Activity Diagram | Shows CRUD operation flow |

