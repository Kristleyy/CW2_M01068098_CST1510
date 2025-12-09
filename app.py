"""
Multi-Domain Intelligence Platform
Main Streamlit Application Entry Point

A unified web application serving Cybersecurity Analysts, Data Scientists, 
and IT Administrators with high-value analysis and insights.
"""

import streamlit as st
from database import DatabaseManager
from auth import AuthManager
import os

# Page configuration - must be the first Streamlit command
st.set_page_config(
    page_title="Multi-Domain Intelligence Platform",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for beautiful, modern UI with high contrast text
st.markdown("""
<style>
    /* Import distinctive fonts */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
    
    /* Root variables for theming */
    :root {
        --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --secondary-gradient: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        --dark-bg: #0f0f1a;
        --card-bg: #1a1a2e;
        --accent-cyan: #00d4ff;
        --accent-purple: #9d4edd;
        --accent-pink: #f72585;
        --text-primary: #ffffff;
        --text-secondary: #e0e0e0;
    }
    
    /* Main app styling */
    .stApp {
        background: linear-gradient(180deg, #1e1e2e 0%, #2d2d44 50%, #1e1e2e 100%);
    }
    
    /* Global text color fix - ensure all text is visible */
    .stApp, .stApp p, .stApp span, .stApp div, .stApp label {
        color: #ffffff !important;
    }
    
    /* Markdown text */
    .stMarkdown, .stMarkdown p, .stMarkdown span, .stMarkdown li {
        color: #ffffff !important;
    }
    
    /* Headers */
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
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
        border-right: 1px solid rgba(157, 78, 221, 0.3);
    }
    
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Radio buttons and labels in sidebar */
    [data-testid="stSidebar"] label {
        color: #ffffff !important;
    }
    
    /* Metric cards */
    [data-testid="stMetric"] {
        background: linear-gradient(145deg, #2d2d44, #1e1e2e);
        border: 1px solid rgba(0, 212, 255, 0.3);
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
    
    [data-testid="stMetric"] label {
        font-family: 'Outfit', sans-serif !important;
        color: #e0e0e0 !important;
    }
    
    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        font-family: 'JetBrains Mono', monospace !important;
        color: #00d4ff !important;
    }
    
    [data-testid="stMetric"] [data-testid="stMetricDelta"] {
        color: #a0e0a0 !important;
    }
    
    /* Buttons */
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
    
    /* Input fields */
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
    
    .stTextInput > div > div > input:focus {
        border-color: #00d4ff;
        box-shadow: 0 0 15px rgba(0, 212, 255, 0.3);
    }
    
    .stTextInput > div > div > input::placeholder {
        color: #a0a0b0 !important;
    }
    
    /* Number inputs */
    .stNumberInput label {
        color: #ffffff !important;
    }
    
    .stNumberInput input {
        background: rgba(45, 45, 68, 0.9) !important;
        color: #ffffff !important;
        border: 1px solid rgba(157, 78, 221, 0.4);
    }
    
    /* Select boxes */
    .stSelectbox label {
        color: #ffffff !important;
    }
    
    .stSelectbox > div > div {
        background: rgba(45, 45, 68, 0.9) !important;
        border: 1px solid rgba(157, 78, 221, 0.4);
        border-radius: 12px;
        color: #ffffff !important;
    }
    
    .stSelectbox [data-baseweb="select"] span {
        color: #ffffff !important;
    }
    
    /* Multiselect */
    .stMultiSelect label {
        color: #ffffff !important;
    }
    
    .stMultiSelect > div > div {
        background: rgba(45, 45, 68, 0.9) !important;
        border: 1px solid rgba(157, 78, 221, 0.4);
        color: #ffffff !important;
    }
    
    /* Slider */
    .stSlider label {
        color: #ffffff !important;
    }
    
    .stSlider [data-baseweb="slider"] div {
        color: #ffffff !important;
    }
    
    /* Text area */
    .stTextArea label {
        color: #ffffff !important;
    }
    
    .stTextArea textarea {
        background: rgba(45, 45, 68, 0.9) !important;
        color: #ffffff !important;
        border: 1px solid rgba(157, 78, 221, 0.4);
    }
    
    /* Radio buttons */
    .stRadio label {
        color: #ffffff !important;
    }
    
    .stRadio [data-baseweb="radio"] label {
        color: #ffffff !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: transparent;
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        font-family: 'Outfit', sans-serif;
        background: rgba(45, 45, 68, 0.8);
        border-radius: 10px;
        color: #e0e0e0 !important;
        border: 1px solid transparent;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.4), rgba(118, 75, 162, 0.4));
        color: #ffffff !important;
        border: 1px solid rgba(0, 212, 255, 0.5);
    }
    
    /* Dataframes */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
    }
    
    .stDataFrame [data-testid="stDataFrameResizable"] {
        background: rgba(45, 45, 68, 0.5);
    }
    
    /* Expanders */
    .streamlit-expanderHeader {
        font-family: 'Outfit', sans-serif;
        background: rgba(45, 45, 68, 0.8);
        border-radius: 12px;
        color: #ffffff !important;
    }
    
    details summary span {
        color: #ffffff !important;
    }
    
    /* Success/Error messages */
    .stSuccess {
        background-color: rgba(6, 214, 160, 0.2) !important;
        color: #06d6a0 !important;
        border-radius: 12px;
    }
    
    .stError {
        background-color: rgba(247, 37, 133, 0.2) !important;
        color: #f72585 !important;
        border-radius: 12px;
    }
    
    .stWarning {
        background-color: rgba(255, 209, 102, 0.2) !important;
        color: #ffd166 !important;
        border-radius: 12px;
    }
    
    .stInfo {
        background-color: rgba(0, 212, 255, 0.2) !important;
        color: #00d4ff !important;
        border-radius: 12px;
    }
    
    /* Chat messages */
    .stChatMessage {
        background: rgba(45, 45, 68, 0.8);
        border-radius: 16px;
        border: 1px solid rgba(157, 78, 221, 0.3);
    }
    
    .stChatMessage p {
        color: #ffffff !important;
    }
    
    /* Chat input */
    .stChatInput input {
        background: rgba(45, 45, 68, 0.9) !important;
        color: #ffffff !important;
        border: 1px solid rgba(157, 78, 221, 0.4);
    }
    
    /* Form styling */
    [data-testid="stForm"] {
        background: rgba(45, 45, 68, 0.5);
        border: 1px solid rgba(157, 78, 221, 0.3);
        border-radius: 16px;
        padding: 20px;
    }
    
    /* Table/dataframe text */
    .stDataFrame td, .stDataFrame th {
        color: #ffffff !important;
    }
    
    /* Plotly chart backgrounds */
    .js-plotly-plot .plotly .bg {
        fill: transparent !important;
    }
</style>
""", unsafe_allow_html=True)


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
        # Login/Register tabs
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
        
        with tab1:
            st.markdown("### Welcome Back")
            login_username = st.text_input("Username", key="login_user", placeholder="Enter your username")
            login_password = st.text_input("Password", type="password", key="login_pass", placeholder="Enter your password")
            
            if st.button("Login", key="login_btn", use_container_width=True):
                if login_username and login_password:
                    # First try database
                    user = st.session_state.db.get_user(login_username)
                    if user:
                        from auth import AuthManager
                        auth = AuthManager()
                        if auth.verify_password(login_password, user[2]):
                            st.session_state.authenticated = True
                            st.session_state.user = {
                                'username': user[1],
                                'role': user[3]
                            }
                            st.success("✓ Login successful!")
                            st.rerun()
                        else:
                            st.error("❌ Invalid username or password.")
                    else:
                        # Try file-based auth
                        success, message, user_data = st.session_state.auth.login(login_username, login_password)
                        if success:
                            st.session_state.authenticated = True
                            st.session_state.user = user_data
                            st.success("✓ Login successful!")
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
                "Role",
                ["cybersecurity", "datascience", "it_operations", "admin"],
                format_func=lambda x: {
                    "cybersecurity": "🛡️ Cybersecurity Analyst",
                    "datascience": "📊 Data Scientist", 
                    "it_operations": "🖥️ IT Administrator",
                    "admin": "👑 Administrator"
                }.get(x, x)
            )
            
            if st.button("Register", key="reg_btn", use_container_width=True):
                if reg_password != reg_password2:
                    st.error("❌ Passwords do not match.")
                elif len(reg_password) < 8:
                    st.error("❌ Password must be at least 8 characters.")
                elif reg_username and reg_password:
                    # Register in database
                    password_hash = st.session_state.auth.hash_password(reg_password)
                    if st.session_state.db.create_user(reg_username, password_hash, reg_role):
                        st.success("✓ Registration successful! Please login.")
                    else:
                        st.error("❌ Username already exists.")
                else:
                    st.warning("⚠️ Please fill in all fields.")
        
        # Demo credentials info
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; color: #e0e0e0; font-size: 0.9rem;">
            <p><strong style="color: #ffffff;">First time?</strong> Register a new account above.</p>
        </div>
        """, unsafe_allow_html=True)


def get_allowed_pages(role: str) -> list:
    """Get list of pages allowed for a specific role."""
    role_permissions = {
        "admin": ["🏠 Home", "🛡️ Cybersecurity", "📊 Data Science", "🖥️ IT Operations"],
        "cybersecurity": ["🛡️ Cybersecurity"],
        "datascience": ["📊 Data Science"],
        "it_operations": ["🖥️ IT Operations"]
    }
    return role_permissions.get(role, [])


def main_dashboard():
    """Display the main dashboard after login."""
    user = st.session_state.user
    user_role = user.get('role', '')
    
    # Get allowed pages for this user's role
    allowed_pages = get_allowed_pages(user_role)
    
    # Sidebar
    with st.sidebar:
        st.markdown(f"""
        <div style="padding: 20px 0; text-align: center;">
            <h2 style="margin: 0; color: #ffffff;">🔮 MDIP</h2>
            <p style="color: #e0e0e0; font-size: 0.9rem;">Multi-Domain Intelligence</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # User info
        role_icons = {
            "admin": "👑",
            "cybersecurity": "🛡️",
            "datascience": "📊",
            "it_operations": "🖥️"
        }
        role_icon = role_icons.get(user_role, "👤")
        
        role_display = {
            "admin": "Administrator (Full Access)",
            "cybersecurity": "Cybersecurity Analyst",
            "datascience": "Data Scientist",
            "it_operations": "IT Administrator"
        }
        
        st.markdown(f"""
        <div style="padding: 15px; background: rgba(45, 45, 68, 0.8); border-radius: 12px; margin-bottom: 20px; border: 1px solid rgba(157, 78, 221, 0.3);">
            <p style="margin: 0; font-size: 0.9rem; color: #e0e0e0;">Logged in as</p>
            <p style="margin: 5px 0; font-size: 1.1rem; font-weight: 600; color: #ffffff;">{role_icon} {user.get('username', 'User')}</p>
            <p style="margin: 0; font-size: 0.85rem; color: #00d4ff;">{role_display.get(user_role, user_role)}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Navigation - Only show allowed pages
        if len(allowed_pages) > 1:
            st.markdown("### Navigation")
            page = st.radio(
                "Select Dashboard",
                allowed_pages,
                label_visibility="collapsed"
            )
        else:
            # Single domain user - no navigation needed
            page = allowed_pages[0] if allowed_pages else "🏠 Home"
            st.markdown(f"""
            <div style="padding: 10px; background: rgba(0, 212, 255, 0.1); border-radius: 8px; border: 1px solid rgba(0, 212, 255, 0.3);">
                <p style="margin: 0; color: #e0e0e0; font-size: 0.85rem;">📍 Your Dashboard</p>
                <p style="margin: 5px 0 0 0; color: #ffffff; font-weight: 500;">{page}</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Quick actions
        st.markdown("### Quick Actions")
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.session_state.db.load_all_sample_data()
            st.success("Data refreshed!")
            
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.user = None
            st.session_state.chat_history = []
            st.rerun()
    
    # Main content area - enforce access control
    if "Home" in page and "🏠 Home" in allowed_pages:
        show_home_page()
    elif "Cybersecurity" in page and "🛡️ Cybersecurity" in allowed_pages:
        show_cybersecurity_dashboard()
    elif "Data Science" in page and "📊 Data Science" in allowed_pages:
        show_datascience_dashboard()
    elif "IT Operations" in page and "🖥️ IT Operations" in allowed_pages:
        show_it_operations_dashboard()
    else:
        # Fallback - show the first allowed page
        if "🛡️ Cybersecurity" in allowed_pages:
            show_cybersecurity_dashboard()
        elif "📊 Data Science" in allowed_pages:
            show_datascience_dashboard()
        elif "🖥️ IT Operations" in allowed_pages:
            show_it_operations_dashboard()
        else:
            st.error("⛔ Access Denied. You don't have permission to view any dashboards.")


def show_home_page():
    """Display the home page with overview metrics (Admin only)."""
    st.markdown("# 🏠 Platform Overview")
    st.markdown("*Administrator Dashboard - Full platform visibility*")
    
    # Load stats
    db = st.session_state.db
    incident_stats = db.get_incident_stats()
    dataset_stats = db.get_dataset_stats()
    ticket_stats = db.get_ticket_stats()
    
    # Overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Security Incidents",
            value=incident_stats['total'],
            delta=f"{incident_stats['by_status'].get('Open', 0)} open"
        )
    
    with col2:
        st.metric(
            label="Datasets Managed",
            value=dataset_stats['total'],
            delta=f"{dataset_stats['total_size_gb']} GB total"
        )
    
    with col3:
        st.metric(
            label="IT Tickets",
            value=ticket_stats['total'],
            delta=f"{ticket_stats['by_status'].get('In Progress', 0)} in progress"
        )
    
    with col4:
        st.metric(
            label="SLA Compliance",
            value=f"{ticket_stats['sla_compliance']}%",
            delta="Target: 95%"
        )
    
    st.markdown("---")
    
    # Domain cards
    st.markdown("### Domain Dashboards")
    st.markdown("*Select a dashboard from the sidebar to view detailed analytics*")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="padding: 25px; background: linear-gradient(145deg, rgba(247, 37, 133, 0.15), rgba(157, 78, 221, 0.15)); 
                    border-radius: 16px; border: 1px solid rgba(247, 37, 133, 0.4); height: 200px;">
            <h3 style="margin: 0 0 15px 0; color: #ffffff;">🛡️ Cybersecurity</h3>
            <p style="color: #e0e0e0; font-size: 0.95rem;">
                Analyze security incidents, identify threat trends, and optimize incident response.
            </p>
            <p style="color: #ff6b9d; margin-top: 15px;">
                <strong>{} incidents</strong> • {} unresolved
            </p>
        </div>
        """.format(
            incident_stats['total'],
            incident_stats['by_status'].get('Open', 0) + incident_stats['by_status'].get('In Progress', 0)
        ), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="padding: 25px; background: linear-gradient(145deg, rgba(0, 212, 255, 0.15), rgba(102, 126, 234, 0.15)); 
                    border-radius: 16px; border: 1px solid rgba(0, 212, 255, 0.4); height: 200px;">
            <h3 style="margin: 0 0 15px 0; color: #ffffff;">📊 Data Science</h3>
            <p style="color: #e0e0e0; font-size: 0.95rem;">
                Manage dataset catalog, enforce data governance, and analyze resource consumption.
            </p>
            <p style="color: #4de8ff; margin-top: 15px;">
                <strong>{} datasets</strong> • {} GB storage
            </p>
        </div>
        """.format(
            dataset_stats['total'],
            dataset_stats['total_size_gb']
        ), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="padding: 25px; background: linear-gradient(145deg, rgba(157, 78, 221, 0.15), rgba(102, 126, 234, 0.15)); 
                    border-radius: 16px; border: 1px solid rgba(157, 78, 221, 0.4); height: 200px;">
            <h3 style="margin: 0 0 15px 0; color: #ffffff;">🖥️ IT Operations</h3>
            <p style="color: #e0e0e0; font-size: 0.95rem;">
                Monitor service desk performance, identify bottlenecks, and optimize resolution times.
            </p>
            <p style="color: #c77dff; margin-top: 15px;">
                <strong>{} tickets</strong> • {}h avg resolution
            </p>
        </div>
        """.format(
            ticket_stats['total'],
            ticket_stats['avg_resolution_hours']
        ), unsafe_allow_html=True)


def show_cybersecurity_dashboard():
    """Display the Cybersecurity dashboard."""
    from dashboards.cybersecurity import render_cybersecurity_page
    render_cybersecurity_page()


def show_datascience_dashboard():
    """Display the Data Science dashboard."""
    from dashboards.datascience import render_datascience_page
    render_datascience_page()


def show_it_operations_dashboard():
    """Display the IT Operations dashboard."""
    from dashboards.it_operations import render_it_operations_page
    render_it_operations_page()


def main():
    """Main application entry point."""
    init_session_state()
    
    # Ensure data is loaded
    db = st.session_state.db
    if db.get_incident_stats()['total'] == 0:
        db.load_all_sample_data()
    
    if not st.session_state.authenticated:
        login_page()
    else:
        main_dashboard()


if __name__ == "__main__":
    main()

