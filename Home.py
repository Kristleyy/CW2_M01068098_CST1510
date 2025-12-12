"""
Multi-Domain Intelligence Platform
Login Page - Main Entry Point

Users are directed to their domain-specific dashboard after login.
"""

import streamlit as st
from database import DatabaseManager
from auth import AuthManager

# Page configuration - must be the first Streamlit command
st.set_page_config(
    page_title="Login - Multi-Domain Intelligence Platform",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)


def init_session_state():
    """Initialize session state variables."""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'db' not in st.session_state:
        st.session_state.db = DatabaseManager()
    if 'auth' not in st.session_state:
        st.session_state.auth = AuthManager()
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []


# Initialize session state FIRST
init_session_state()

# Ensure data is loaded
if st.session_state.db.get_incident_stats()['total'] == 0:
    st.session_state.db.load_all_sample_data("DATA")


# Custom CSS - different based on login state
if not st.session_state.authenticated:
    # Hide sidebar when not logged in
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
        
        .stApp {
            background: linear-gradient(180deg, #1e1e2e 0%, #2d2d44 50%, #1e1e2e 100%);
        }
        
        .stApp, .stApp p, .stApp span, .stApp div, .stApp label {
            color: #ffffff !important;
        }
        
        .stMarkdown, .stMarkdown p, .stMarkdown span, .stMarkdown li {
            color: #ffffff !important;
        }
        
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Outfit', sans-serif !important;
            font-weight: 600 !important;
            color: #ffffff !important;
        }
        
        h1 {
            background: linear-gradient(135deg, #00d4ff 0%, #9d4edd 50%, #f72585 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        /* Hide sidebar when not logged in */
        [data-testid="stSidebar"] {
            display: none;
        }
        
        .stButton > button {
            font-family: 'Outfit', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white !important;
            border: none;
            border-radius: 12px;
            padding: 12px 28px;
            font-weight: 500;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6);
            color: white !important;
        }
        
        .stTextInput > div > div > input {
            font-family: 'Outfit', sans-serif;
            background: rgba(45, 45, 68, 0.9) !important;
            border: 1px solid rgba(157, 78, 221, 0.4);
            border-radius: 12px;
            color: #ffffff !important;
        }
        
        .stTextInput label {
            color: #ffffff !important;
        }
        
        .stSelectbox label {
            color: #ffffff !important;
        }
        
        .stSelectbox > div > div {
            background: rgba(45, 45, 68, 0.9) !important;
            border: 1px solid rgba(157, 78, 221, 0.4);
            border-radius: 12px;
            color: #ffffff !important;
        }
        
        .stTabs [data-baseweb="tab-list"] {
            background: transparent;
            gap: 8px;
        }
        
        .stTabs [data-baseweb="tab"] {
            font-family: 'Outfit', sans-serif;
            background: rgba(45, 45, 68, 0.8);
            border-radius: 10px;
            color: #e0e0e0 !important;
        }
        
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.4), rgba(118, 75, 162, 0.4));
            color: #ffffff !important;
            border: 1px solid rgba(0, 212, 255, 0.5);
        }
        
        .stSuccess { background-color: rgba(6, 214, 160, 0.2) !important; border-radius: 12px; }
        .stError { background-color: rgba(247, 37, 133, 0.2) !important; border-radius: 12px; }
        .stWarning { background-color: rgba(255, 209, 102, 0.2) !important; border-radius: 12px; }
        .stInfo { background-color: rgba(0, 212, 255, 0.2) !important; border-radius: 12px; }
    </style>
    """, unsafe_allow_html=True)
else:
    # Show sidebar when logged in
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
        
        .stApp {
            background: linear-gradient(180deg, #1e1e2e 0%, #2d2d44 50%, #1e1e2e 100%);
        }
        
        .stApp, .stApp p, .stApp span, .stApp div, .stApp label {
            color: #ffffff !important;
        }
        
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Outfit', sans-serif !important;
            font-weight: 600 !important;
            color: #ffffff !important;
        }
        
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
            border-right: 1px solid rgba(157, 78, 221, 0.3);
        }
        
        [data-testid="stSidebar"] * {
            color: #ffffff !important;
        }
        
        .stButton > button {
            font-family: 'Outfit', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white !important;
            border: none;
            border-radius: 12px;
            padding: 12px 28px;
            font-weight: 500;
        }
        
        .stSuccess { background-color: rgba(6, 214, 160, 0.2) !important; border-radius: 12px; }
        .stError { background-color: rgba(247, 37, 133, 0.2) !important; border-radius: 12px; }
    </style>
    """, unsafe_allow_html=True)


def login_page():
    """Display the login page."""
    st.markdown("""
    <div style="text-align: center; padding: 40px 0;">
        <h1 style="font-size: 3rem; margin-bottom: 10px;">🔮 Multi-Domain Intelligence Platform</h1>
        <p style="color: #e0e0e0; font-size: 1.2rem; font-family: 'Outfit', sans-serif;">
            Unified Analytics for Security, Data Science & IT Operations
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
        
        with tab1:
            st.markdown("### Welcome Back")
            login_username = st.text_input("Username", key="login_user", placeholder="Enter your username")
            login_password = st.text_input("Password", type="password", key="login_pass", placeholder="Enter your password")
            
            if st.button("Login", key="login_btn", use_container_width=True):
                if login_username and login_password:
                    user = st.session_state.db.get_user(login_username)
                    if user:
                        auth = AuthManager()
                        if auth.verify_password(login_password, user[2]):
                            st.session_state.authenticated = True
                            st.session_state.user = {
                                'username': user[1],
                                'role': user[3]
                            }
                            st.rerun()
                        else:
                            st.error("❌ Invalid username or password.")
                    else:
                        success, message, user_data = st.session_state.auth.login(login_username, login_password)
                        if success:
                            st.session_state.authenticated = True
                            st.session_state.user = user_data
                            st.rerun()
                        else:
                            st.error(f"❌ {message}")
                else:
                    st.warning("⚠️ Please enter both username and password.")
        
        with tab2:
            st.markdown("### Create Account")
            reg_username = st.text_input("Username", key="reg_user", placeholder="Choose a username")
            reg_password = st.text_input("Password", type="password", key="reg_pass", placeholder="Min. 8 characters")
            reg_password2 = st.text_input("Confirm Password", type="password", key="reg_pass2", placeholder="Confirm your password")
            reg_role = st.selectbox(
                "Select Your Domain",
                ["cybersecurity", "datascience", "it_operations"],
                format_func=lambda x: {
                    "cybersecurity": "🛡️ Cybersecurity Analyst",
                    "datascience": "📊 Data Scientist", 
                    "it_operations": "🖥️ IT Administrator"
                }.get(x, x)
            )
            
            if st.button("Register", key="reg_btn", use_container_width=True):
                if reg_password != reg_password2:
                    st.error("❌ Passwords do not match.")
                elif len(reg_password) < 8:
                    st.error("❌ Password must be at least 8 characters.")
                elif reg_username and reg_password:
                    password_hash = st.session_state.auth.hash_password(reg_password)
                    if st.session_state.db.create_user(reg_username, password_hash, reg_role):
                        st.success("✓ Registration successful! Please login.")
                    else:
                        st.error("❌ Username already exists.")
                else:
                    st.warning("⚠️ Please fill in all fields.")
        
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; color: #e0e0e0; font-size: 0.9rem;">
            <p><strong style="color: #ffffff;">First time?</strong> Register a new account above.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("### Available Domains")
        
        col_a, col_b, col_c = st.columns(3)
        
        with col_a:
            st.markdown("""
            <div style="padding: 20px; background: linear-gradient(145deg, rgba(247, 37, 133, 0.15), rgba(157, 78, 221, 0.15)); 
                        border-radius: 16px; border: 1px solid rgba(247, 37, 133, 0.4); text-align: center;">
                <h4 style="margin: 0 0 10px 0; color: #ffffff;">🛡️ Cybersecurity</h4>
                <p style="color: #e0e0e0; font-size: 0.85rem; margin: 0;">Incident response & threat analysis</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col_b:
            st.markdown("""
            <div style="padding: 20px; background: linear-gradient(145deg, rgba(0, 212, 255, 0.15), rgba(102, 126, 234, 0.15)); 
                        border-radius: 16px; border: 1px solid rgba(0, 212, 255, 0.4); text-align: center;">
                <h4 style="margin: 0 0 10px 0; color: #ffffff;">📊 Data Science</h4>
                <p style="color: #e0e0e0; font-size: 0.85rem; margin: 0;">Data governance & discovery</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col_c:
            st.markdown("""
            <div style="padding: 20px; background: linear-gradient(145deg, rgba(157, 78, 221, 0.15), rgba(102, 126, 234, 0.15)); 
                        border-radius: 16px; border: 1px solid rgba(157, 78, 221, 0.4); text-align: center;">
                <h4 style="margin: 0 0 10px 0; color: #ffffff;">🖥️ IT Operations</h4>
                <p style="color: #e0e0e0; font-size: 0.85rem; margin: 0;">Service desk performance</p>
            </div>
            """, unsafe_allow_html=True)


def logged_in_page():
    """Display the logged-in page with navigation."""
    user = st.session_state.user
    role = user.get('role', 'cybersecurity')
    
    # Sidebar with navigation
    with st.sidebar:
        st.markdown("""
        <div style="padding: 20px 0; text-align: center;">
            <h2 style="margin: 0; color: #9d4edd;">🔮 MDIP</h2>
            <p style="color: #e0e0e0; font-size: 0.9rem;">Multi-Domain Intelligence</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        role_icons = {"cybersecurity": "🛡️", "datascience": "📊", "it_operations": "🖥️", "admin": "👑"}
        role_names = {"cybersecurity": "Cybersecurity Analyst", "datascience": "Data Scientist", "it_operations": "IT Administrator", "admin": "Administrator"}
        
        st.markdown(f"""
        <div style="padding: 15px; background: rgba(157, 78, 221, 0.1); border-radius: 12px; margin-bottom: 20px; border: 1px solid rgba(157, 78, 221, 0.3);">
            <p style="margin: 0; font-size: 0.9rem; color: #e0e0e0;">Logged in as</p>
            <p style="margin: 5px 0; font-size: 1.1rem; font-weight: 600; color: #ffffff;">{role_icons.get(role, '👤')} {user.get('username', 'User')}</p>
            <p style="margin: 0; font-size: 0.85rem; color: #9d4edd;">{role_names.get(role, role)}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 📍 Your Dashboard")
        st.info(f"Click on **{role_icons.get(role, '')} {role.replace('_', ' ').title()}** in the sidebar above to access your dashboard.")
        
        st.markdown("---")
        
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.user = None
            st.session_state.chat_history = []
            st.rerun()
    
    # Main content
    role_display = {
        "cybersecurity": ("🛡️ Cybersecurity Dashboard", "cybersecurity", "#f72585"),
        "datascience": ("📊 Data Science Dashboard", "datascience", "#00d4ff"),
        "it_operations": ("🖥️ IT Operations Dashboard", "it_operations", "#9d4edd"),
        "admin": ("🛡️ Cybersecurity Dashboard", "cybersecurity", "#f72585")
    }
    
    dashboard_name, page_name, color = role_display.get(role, ("Dashboard", "cybersecurity", "#9d4edd"))
    
    st.markdown(f"""
    <div style="text-align: center; padding: 80px 20px;">
        <h1 style="font-size: 2.5rem; margin-bottom: 20px;">✅ You are logged in!</h1>
        <p style="color: #e0e0e0; font-size: 1.3rem; margin-bottom: 10px;">
            Welcome, <strong style="color: #00d4ff;">{user.get('username', 'User')}</strong>
        </p>
        <p style="color: #a0a0b0; font-size: 1.1rem; margin-bottom: 40px;">
            Your assigned dashboard: <strong style="color: {color};">{dashboard_name}</strong>
        </p>
        <div style="padding: 30px; background: rgba(45, 45, 68, 0.5); border-radius: 16px; border: 1px solid rgba(157, 78, 221, 0.3); max-width: 500px; margin: 0 auto;">
            <p style="color: #ffffff; font-size: 1.1rem; margin: 0;">
                👈 Click on <strong style="color: {color};">{page_name}</strong> in the <strong>sidebar</strong> to access your dashboard
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)


# Main logic
if st.session_state.authenticated and st.session_state.user:
    logged_in_page()
else:
    login_page()
