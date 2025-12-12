"""
Cybersecurity Domain Dashboard
Addresses: Incident Response Bottleneck - Phishing surge analysis
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Page configuration - MUST be first Streamlit command
st.set_page_config(
    page_title="Cybersecurity - MDIP",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import shared components
import sys
sys.path.insert(0, '..')
from database import DatabaseManager
from auth import AuthManager

# Custom CSS
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
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
        border-right: 1px solid rgba(247, 37, 133, 0.3);
    }
    
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    
    [data-testid="stMetric"] {
        background: linear-gradient(145deg, #2d2d44, #1e1e2e);
        border: 1px solid rgba(247, 37, 133, 0.3);
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
    
    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        font-family: 'JetBrains Mono', monospace !important;
        color: #f72585 !important;
    }
    
    .stButton > button {
        font-family: 'Outfit', sans-serif;
        background: linear-gradient(135deg, #f72585 0%, #b5179e 100%);
        color: white !important;
        border: none;
        border-radius: 12px;
        padding: 12px 28px;
        font-weight: 500;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(247, 37, 133, 0.4);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(247, 37, 133, 0.6);
    }
    
    .stTextInput > div > div > input, .stSelectbox > div > div, .stMultiSelect > div > div, .stTextArea textarea {
        background: rgba(45, 45, 68, 0.9) !important;
        border: 1px solid rgba(247, 37, 133, 0.4);
        border-radius: 12px;
        color: #ffffff !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: rgba(45, 45, 68, 0.8);
        border-radius: 10px;
        color: #e0e0e0 !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(247, 37, 133, 0.4), rgba(181, 23, 158, 0.4));
        color: #ffffff !important;
        border: 1px solid rgba(247, 37, 133, 0.5);
    }
    
    .stDataFrame { border-radius: 12px; overflow: hidden; }
    
    .stSuccess { background-color: rgba(6, 214, 160, 0.2) !important; border-radius: 12px; }
    .stError { background-color: rgba(247, 37, 133, 0.2) !important; border-radius: 12px; }
    .stWarning { background-color: rgba(255, 209, 102, 0.2) !important; border-radius: 12px; }
    .stInfo { background-color: rgba(247, 37, 133, 0.2) !important; border-radius: 12px; }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialize session state if needed."""
    if 'db' not in st.session_state:
        st.session_state.db = DatabaseManager()
    if 'auth' not in st.session_state:
        st.session_state.auth = AuthManager()
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user' not in st.session_state:
        st.session_state.user = None


def check_authentication():
    """Check if user is authenticated and has access to this page."""
    if not st.session_state.get('authenticated', False):
        st.warning("⚠️ Please login first to access this dashboard.")
        st.markdown("""
        <div style="text-align: center; padding: 40px;">
            <p style="color: #a0a0b0;">Go to the main app page to login.</p>
        </div>
        """, unsafe_allow_html=True)
        st.stop()
    
    user_role = st.session_state.user.get('role', '') if st.session_state.user else ''
    allowed_roles = ['cybersecurity', 'admin']
    
    if user_role not in allowed_roles:
        st.error(f"⛔ Access Denied. Your role ({user_role}) does not have permission to access the Cybersecurity dashboard.")
        st.stop()


def render_sidebar():
    """Render the sidebar with user info and logout."""
    with st.sidebar:
        st.markdown("""
        <div style="padding: 20px 0; text-align: center;">
            <h2 style="margin: 0; color: #f72585;">🛡️ Cybersecurity</h2>
            <p style="color: #e0e0e0; font-size: 0.9rem;">Incident Response Center</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        user = st.session_state.user
        st.markdown(f"""
        <div style="padding: 15px; background: rgba(247, 37, 133, 0.1); border-radius: 12px; margin-bottom: 20px; border: 1px solid rgba(247, 37, 133, 0.3);">
            <p style="margin: 0; font-size: 0.9rem; color: #e0e0e0;">Logged in as</p>
            <p style="margin: 5px 0; font-size: 1.1rem; font-weight: 600; color: #ffffff;">🛡️ {user.get('username', 'User')}</p>
            <p style="margin: 0; font-size: 0.85rem; color: #f72585;">Cybersecurity Analyst</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### Quick Actions")
        
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.session_state.db.load_all_sample_data("DATA")
            st.success("Data refreshed!")
            st.rerun()
        
        st.markdown("---")
        
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.user = None
            st.session_state.chat_history = []
            st.rerun()


def render_cybersecurity_page():
    """Render the Cybersecurity dashboard."""
    st.markdown("# 🛡️ Cybersecurity Dashboard")
    st.markdown("*Incident Response & Threat Analysis*")
    
    db = st.session_state.db
    df = db.get_incidents_dataframe()
    
    if df.empty:
        st.warning("No incident data available. Please load sample data.")
        if st.button("Load Sample Data"):
            db.load_all_sample_data("DATA")
            st.rerun()
        return
    
    df['created_at'] = pd.to_datetime(df['created_at'])
    df['resolved_at'] = pd.to_datetime(df['resolved_at'])
    
    stats = db.get_incident_stats()
    
    # KEY METRICS
    st.markdown("### 📈 Key Metrics")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Incidents", stats['total'], help="Total number of security incidents")
    with col2:
        open_incidents = stats['by_status'].get('Open', 0) + stats['by_status'].get('In Progress', 0)
        st.metric("Open/In Progress", open_incidents, delta=f"-{stats['by_status'].get('Resolved', 0)} resolved", delta_color="inverse")
    with col3:
        critical_count = stats['by_severity'].get('Critical', 0)
        st.metric("Critical Severity", critical_count, delta="Requires immediate attention" if critical_count > 0 else "All clear", delta_color="inverse" if critical_count > 0 else "normal")
    with col4:
        phishing_count = stats['by_threat_type'].get('Phishing', 0)
        phishing_pct = round(phishing_count / stats['total'] * 100, 1) if stats['total'] > 0 else 0
        st.metric("Phishing Incidents", phishing_count, delta=f"{phishing_pct}% of total", delta_color="inverse")
    with col5:
        st.metric("Avg Resolution Time", f"{stats['avg_resolution_hours']}h", help="Average time to resolve incidents")
    
    st.markdown("---")
    
    # TABS
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Analytics", "🔍 Incident Explorer", "➕ Manage Incidents", "🤖 AI Assistant"])
    
    with tab1:
        render_analytics_tab(df, stats)
    with tab2:
        render_explorer_tab(df)
    with tab3:
        render_crud_tab(db)
    with tab4:
        render_ai_tab(stats)


def render_analytics_tab(df: pd.DataFrame, stats: dict):
    """Render analytics visualizations."""
    st.markdown("### 🎯 Critical Finding: Phishing Surge Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        threat_df = pd.DataFrame({'Threat Type': list(stats['by_threat_type'].keys()), 'Count': list(stats['by_threat_type'].values())}).sort_values('Count', ascending=False)
        colors = ['#f72585' if t == 'Phishing' else '#4361ee' for t in threat_df['Threat Type']]
        fig = px.bar(threat_df, x='Threat Type', y='Count', title='Threat Type Distribution', color='Threat Type', color_discrete_sequence=colors)
        fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='white'), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        phishing_df = df[df['threat_type'] == 'Phishing']
        if not phishing_df.empty:
            phishing_status = phishing_df['status'].value_counts()
            fig = px.pie(values=phishing_status.values, names=phishing_status.index, title='Phishing Incidents by Status', color_discrete_sequence=['#f72585', '#ffd166', '#06d6a0'], hole=0.4)
            fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='white'))
            st.plotly_chart(fig, use_container_width=True)
    
    phishing_df = df[df['threat_type'] == 'Phishing']
    unresolved_phishing = len(phishing_df[phishing_df['status'] != 'Resolved']) if not phishing_df.empty else 0
    st.markdown(f"""
    <div style="padding: 20px; background: linear-gradient(145deg, rgba(247, 37, 133, 0.2), rgba(247, 37, 133, 0.1)); 
                border-radius: 16px; border-left: 4px solid #f72585; margin: 20px 0;">
        <h4 style="color: #f72585; margin: 0 0 10px 0;">⚠️ Phishing Surge Detected</h4>
        <p style="color: white; margin: 0;">
            <strong>{stats['by_threat_type'].get('Phishing', 0)}</strong> phishing incidents identified, 
            representing <strong>{round(stats['by_threat_type'].get('Phishing', 0) / stats['total'] * 100, 1) if stats['total'] > 0 else 0}%</strong> of all incidents.
            <strong>{unresolved_phishing}</strong> remain unresolved.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### 📅 Incident Timeline")
    
    df['date'] = df['created_at'].dt.date
    daily_counts = df.groupby(['date', 'threat_type']).size().reset_index(name='count')
    fig = px.area(daily_counts, x='date', y='count', color='threat_type', title='Daily Incident Volume by Threat Type',
                  color_discrete_map={'Phishing': '#f72585', 'Malware': '#4361ee', 'Unauthorized Access': '#06d6a0', 
                                     'Data Breach': '#ffd166', 'Web Attack': '#4cc9f0', 'DDoS': '#9d4edd', 'Zero-Day': '#f94144'})
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='white'))
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    st.markdown("### ⏱️ Resolution Time Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        resolved_df = df[df['resolved_at'].notna()].copy()
        if not resolved_df.empty:
            resolution_by_threat = resolved_df.groupby('threat_type')['resolution_time_hours'].mean().sort_values(ascending=True)
            fig = px.bar(x=resolution_by_threat.values, y=resolution_by_threat.index, orientation='h', title='Avg Resolution Time by Threat Type (hours)', color=resolution_by_threat.values, color_continuous_scale='RdYlGn_r')
            fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='white'), showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        resolved_df = df[df['resolved_at'].notna()].copy()
        if not resolved_df.empty:
            resolution_by_severity = resolved_df.groupby('severity')['resolution_time_hours'].mean()
            severity_order = ['Critical', 'High', 'Medium', 'Low']
            resolution_by_severity = resolution_by_severity.reindex([s for s in severity_order if s in resolution_by_severity.index])
            fig = px.bar(x=resolution_by_severity.index, y=resolution_by_severity.values, title='Avg Resolution Time by Severity (hours)', color=resolution_by_severity.values, color_continuous_scale='RdYlGn_r')
            fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='white'), showlegend=False)
            st.plotly_chart(fig, use_container_width=True)


def render_explorer_tab(df: pd.DataFrame):
    """Render incident explorer with filtering."""
    st.markdown("### 🔍 Incident Explorer")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        status_filter = st.multiselect("Status", options=df['status'].unique().tolist(), default=df['status'].unique().tolist())
    with col2:
        severity_filter = st.multiselect("Severity", options=df['severity'].unique().tolist(), default=df['severity'].unique().tolist())
    with col3:
        threat_filter = st.multiselect("Threat Type", options=df['threat_type'].unique().tolist(), default=df['threat_type'].unique().tolist())
    with col4:
        search_term = st.text_input("Search", placeholder="Search incidents...")
    
    filtered_df = df[(df['status'].isin(status_filter)) & (df['severity'].isin(severity_filter)) & (df['threat_type'].isin(threat_filter))]
    
    if search_term:
        filtered_df = filtered_df[filtered_df['title'].str.contains(search_term, case=False, na=False) | filtered_df['description'].str.contains(search_term, case=False, na=False)]
    
    st.markdown(f"*Showing {len(filtered_df)} of {len(df)} incidents*")
    
    display_cols = ['incident_id', 'title', 'threat_type', 'severity', 'status', 'assigned_to', 'created_at', 'resolution_time_hours']
    st.dataframe(filtered_df[display_cols].sort_values('created_at', ascending=False), use_container_width=True, height=400)


def render_crud_tab(db):
    """Render CRUD operations for incidents."""
    st.markdown("### ➕ Manage Security Incidents")
    
    action = st.radio("Select Action", ["Create New", "Update Existing", "Delete"], horizontal=True)
    
    if action == "Create New":
        with st.form("create_incident_form"):
            st.markdown("#### Create New Incident")
            col1, col2 = st.columns(2)
            with col1:
                new_id = st.text_input("Incident ID", placeholder="e.g., INC031")
                title = st.text_input("Title", placeholder="Incident title")
                threat_type = st.selectbox("Threat Type", ["Phishing", "Malware", "DDoS", "Unauthorized Access", "Data Breach", "Web Attack", "Zero-Day"])
                severity = st.selectbox("Severity", ["Critical", "High", "Medium", "Low"])
            with col2:
                status = st.selectbox("Status", ["Open", "In Progress", "Resolved"])
                assigned_to = st.text_input("Assigned To", placeholder="Analyst name")
                source_ip = st.text_input("Source IP", placeholder="e.g., 192.168.1.1")
                target_system = st.text_input("Target System", placeholder="e.g., WEB-SERVER-01")
            description = st.text_area("Description", placeholder="Incident description")
            
            if st.form_submit_button("Create Incident", use_container_width=True):
                if new_id and title and assigned_to:
                    incident_data = {'incident_id': new_id, 'title': title, 'description': description, 'threat_type': threat_type, 'severity': severity, 'status': status, 'assigned_to': assigned_to, 'created_at': datetime.now().isoformat(), 'source_ip': source_ip, 'target_system': target_system}
                    if db.create_incident(incident_data):
                        st.success(f"✓ Incident {new_id} created successfully!")
                    else:
                        st.error("❌ Failed to create incident. ID may already exist.")
                else:
                    st.warning("⚠️ Please fill in required fields")
    
    elif action == "Update Existing":
        incidents = db.get_all_incidents()
        if incidents:
            incident_ids = [inc[0] for inc in incidents]
            selected_id = st.selectbox("Select Incident to Update", incident_ids)
            
            if selected_id:
                incident = db.get_incident(selected_id)
                with st.form("update_incident_form"):
                    st.markdown(f"#### Update Incident: {selected_id}")
                    col1, col2 = st.columns(2)
                    with col1:
                        new_status = st.selectbox("Status", ["Open", "In Progress", "Resolved"], index=["Open", "In Progress", "Resolved"].index(incident[5]) if incident[5] in ["Open", "In Progress", "Resolved"] else 0)
                        new_severity = st.selectbox("Severity", ["Critical", "High", "Medium", "Low"], index=["Critical", "High", "Medium", "Low"].index(incident[4]) if incident[4] in ["Critical", "High", "Medium", "Low"] else 0)
                    with col2:
                        new_assigned = st.text_input("Assigned To", value=incident[6] or "")
                        resolution_time = st.number_input("Resolution Time (hours)", value=incident[9] or 0.0, min_value=0.0)
                    
                    if st.form_submit_button("Update Incident", use_container_width=True):
                        updates = {'status': new_status, 'severity': new_severity, 'assigned_to': new_assigned}
                        if new_status == "Resolved" and resolution_time > 0:
                            updates['resolved_at'] = datetime.now().isoformat()
                            updates['resolution_time_hours'] = resolution_time
                        if db.update_incident(selected_id, **updates):
                            st.success(f"✓ Incident {selected_id} updated!")
                            st.rerun()
                        else:
                            st.error("❌ Failed to update incident.")
    
    elif action == "Delete":
        incidents = db.get_all_incidents()
        if incidents:
            incident_ids = [inc[0] for inc in incidents]
            selected_id = st.selectbox("Select Incident to Delete", incident_ids)
            
            if selected_id:
                st.warning(f"⚠️ Are you sure you want to delete incident {selected_id}?")
                if st.button("🗑️ Delete Incident", type="primary"):
                    if db.delete_incident(selected_id):
                        st.success(f"✓ Incident {selected_id} deleted!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to delete incident.")


def render_ai_tab(stats: dict):
    """Render AI Assistant tab with chatbox."""
    st.markdown("### 🤖 AI Security Analyst")
    st.markdown("*Domain-restricted AI assistant for cybersecurity analysis*")
    
    # Initialize chat history for this domain
    if 'cyber_chat' not in st.session_state:
        st.session_state.cyber_chat = []
    
    try:
        from ai_assistant import get_domain_assistant
        assistant = get_domain_assistant('cybersecurity')
        db = st.session_state.db
        
        if assistant is None or not assistant.is_configured():
            st.warning("""
            ⚠️ **AI Assistant Not Configured**
            
            To enable AI analysis:
            1. Get a Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey)
            2. Create a `.env` file with: `GEMINI_API_KEY_CYBER=your_key`
            3. Restart the application
            """)
            
            # Show demo chatbox even without API
            st.markdown("---")
            st.markdown("#### 💬 Chat Preview (Demo Mode)")
            _render_demo_chatbox("cyber")
            return
        
        st.info("🔒 This AI can ONLY answer cybersecurity questions.")
        
        # Quick analysis button
        if st.button("🔍 Auto-Analyze Security Incidents", use_container_width=True):
            with st.spinner("Analyzing incidents..."):
                analysis = assistant.analyze_domain_data(db)
                st.session_state.cyber_chat.append({"role": "assistant", "content": f"**📊 Auto-Analysis Results:**\n\n{analysis}"})
                st.rerun()
        
        st.markdown("---")
        st.markdown("#### 💬 Chat with AI Security Analyst")
        
        # Chat container
        chat_container = st.container()
        
        with chat_container:
            # Display chat history
            for i, msg in enumerate(st.session_state.cyber_chat):
                if msg["role"] == "user":
                    st.markdown(f"""
                    <div style="background: rgba(102, 126, 234, 0.2); padding: 12px 16px; border-radius: 12px; margin: 8px 0; border-left: 3px solid #667eea;">
                        <strong style="color: #667eea;">🧑 You:</strong><br>
                        <span style="color: #ffffff;">{msg['content']}</span>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="background: rgba(247, 37, 133, 0.15); padding: 12px 16px; border-radius: 12px; margin: 8px 0; border-left: 3px solid #f72585;">
                        <strong style="color: #f72585;">🤖 AI:</strong><br>
                        <span style="color: #ffffff;">{msg['content']}</span>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Chat input
        st.markdown("---")
        col1, col2 = st.columns([5, 1])
        with col1:
            user_input = st.text_input(
                "Ask about security incidents, threats, or best practices...",
                key="cyber_input",
                placeholder="e.g., What are the most common phishing attack patterns?",
                label_visibility="collapsed"
            )
        with col2:
            send_btn = st.button("Send", key="cyber_send", use_container_width=True)
        
        # Clear chat button
        col_a, col_b, col_c = st.columns([2, 1, 2])
        with col_b:
            if st.button("🗑️ Clear Chat", key="cyber_clear", use_container_width=True):
                st.session_state.cyber_chat = []
                st.rerun()
        
        # Process user input
        if send_btn and user_input:
            st.session_state.cyber_chat.append({"role": "user", "content": user_input})
            
            with st.spinner("🤖 Thinking..."):
                response = assistant.chat(user_input, db)
            
            st.session_state.cyber_chat.append({"role": "assistant", "content": response})
            st.rerun()
    
    except ImportError:
        st.info("AI Assistant module not available. Showing demo chatbox.")
        st.markdown("---")
        _render_demo_chatbox("cyber")


def _render_demo_chatbox(domain: str):
    """Render a demo chatbox when AI is not configured."""
    chat_key = f"{domain}_demo_chat"
    if chat_key not in st.session_state:
        st.session_state[chat_key] = []
    
    # Display demo messages
    for msg in st.session_state[chat_key]:
        role_color = "#667eea" if msg["role"] == "user" else "#f72585"
        role_icon = "🧑 You" if msg["role"] == "user" else "🤖 AI"
        st.markdown(f"""
        <div style="background: rgba(45, 45, 68, 0.5); padding: 12px 16px; border-radius: 12px; margin: 8px 0; border-left: 3px solid {role_color};">
            <strong style="color: {role_color};">{role_icon}:</strong><br>
            <span style="color: #ffffff;">{msg['content']}</span>
        </div>
        """, unsafe_allow_html=True)
    
    # Demo input
    col1, col2 = st.columns([5, 1])
    with col1:
        demo_input = st.text_input("Type a message (demo mode)...", key=f"{domain}_demo_input", label_visibility="collapsed")
    with col2:
        if st.button("Send", key=f"{domain}_demo_send"):
            if demo_input:
                st.session_state[chat_key].append({"role": "user", "content": demo_input})
                st.session_state[chat_key].append({"role": "assistant", "content": "⚠️ AI not configured. Please set up API keys to enable AI responses. See instructions above."})
                st.rerun()


# Main execution
init_session_state()
check_authentication()
render_sidebar()
render_cybersecurity_page()
