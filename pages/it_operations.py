"""
IT Operations Domain Dashboard
Addresses: Service Desk Performance - Staff performance anomaly and process inefficiency analysis
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Page configuration - MUST be first Streamlit command
st.set_page_config(
    page_title="IT Operations - MDIP",
    page_icon="🖥️",
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
        border-right: 1px solid rgba(157, 78, 221, 0.3);
    }
    
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    
    [data-testid="stMetric"] {
        background: linear-gradient(145deg, #2d2d44, #1e1e2e);
        border: 1px solid rgba(157, 78, 221, 0.3);
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
    
    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        font-family: 'JetBrains Mono', monospace !important;
        color: #9d4edd !important;
    }
    
    .stButton > button {
        font-family: 'Outfit', sans-serif;
        background: linear-gradient(135deg, #9d4edd 0%, #7b2cbf 100%);
        color: white !important;
        border: none;
        border-radius: 12px;
        padding: 12px 28px;
        font-weight: 500;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(157, 78, 221, 0.4);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(157, 78, 221, 0.6);
    }
    
    .stTextInput > div > div > input, .stSelectbox > div > div, .stMultiSelect > div > div, .stTextArea textarea {
        background: rgba(45, 45, 68, 0.9) !important;
        border: 1px solid rgba(157, 78, 221, 0.4);
        border-radius: 12px;
        color: #ffffff !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: rgba(45, 45, 68, 0.8);
        border-radius: 10px;
        color: #e0e0e0 !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(157, 78, 221, 0.4), rgba(123, 44, 191, 0.4));
        color: #ffffff !important;
        border: 1px solid rgba(157, 78, 221, 0.5);
    }
    
    .stDataFrame { border-radius: 12px; overflow: hidden; }
    
    .stSuccess { background-color: rgba(6, 214, 160, 0.2) !important; border-radius: 12px; }
    .stError { background-color: rgba(247, 37, 133, 0.2) !important; border-radius: 12px; }
    .stWarning { background-color: rgba(255, 209, 102, 0.2) !important; border-radius: 12px; }
    .stInfo { background-color: rgba(157, 78, 221, 0.2) !important; border-radius: 12px; }
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
    allowed_roles = ['it_operations', 'admin']
    
    if user_role not in allowed_roles:
        st.error(f"⛔ Access Denied. Your role ({user_role}) does not have permission to access the IT Operations dashboard.")
        st.stop()


def render_sidebar():
    """Render the sidebar with user info and logout."""
    with st.sidebar:
        st.markdown("""
        <div style="padding: 20px 0; text-align: center;">
            <h2 style="margin: 0; color: #9d4edd;">🖥️ IT Operations</h2>
            <p style="color: #e0e0e0; font-size: 0.9rem;">Service Desk Center</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        user = st.session_state.user
        st.markdown(f"""
        <div style="padding: 15px; background: rgba(157, 78, 221, 0.1); border-radius: 12px; margin-bottom: 20px; border: 1px solid rgba(157, 78, 221, 0.3);">
            <p style="margin: 0; font-size: 0.9rem; color: #e0e0e0;">Logged in as</p>
            <p style="margin: 5px 0; font-size: 1.1rem; font-weight: 600; color: #ffffff;">🖥️ {user.get('username', 'User')}</p>
            <p style="margin: 0; font-size: 0.85rem; color: #9d4edd;">IT Administrator</p>
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
            st.rerun()


def render_it_operations_page():
    """Render the IT Operations dashboard."""
    st.markdown("# 🖥️ IT Operations Dashboard")
    st.markdown("*Service Desk Performance & Optimization*")
    
    db = st.session_state.db
    df = db.get_tickets_dataframe()
    
    if df.empty:
        st.warning("No ticket data available. Please load sample data.")
        if st.button("Load Sample Data"):
            db.load_all_sample_data("DATA")
            st.rerun()
        return
    
    df['created_at'] = pd.to_datetime(df['created_at'])
    df['first_response_at'] = pd.to_datetime(df['first_response_at'])
    df['resolved_at'] = pd.to_datetime(df['resolved_at'])
    
    stats = db.get_ticket_stats()
    
    # KEY METRICS
    st.markdown("### 📈 Key Metrics")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Tickets", stats['total'])
    with col2:
        open_tickets = stats['by_status'].get('In Progress', 0) + stats['by_status'].get('Waiting for User', 0)
        st.metric("Open Tickets", open_tickets, delta=f"{stats['by_status'].get('Resolved', 0)} resolved", delta_color="off")
    with col3:
        waiting_count = stats['by_status'].get('Waiting for User', 0)
        st.metric("Waiting for User", waiting_count, delta="Bottleneck" if waiting_count > 3 else "Normal", delta_color="inverse" if waiting_count > 3 else "normal")
    with col4:
        st.metric("SLA Compliance", f"{stats['sla_compliance']}%", delta="Target: 95%", delta_color="normal" if stats['sla_compliance'] >= 95 else "inverse")
    with col5:
        st.metric("Avg Resolution", f"{stats['avg_resolution_hours']}h")
    
    st.markdown("---")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Analytics", "🔍 Ticket Explorer", "➕ Manage Tickets", "🤖 AI Assistant"])
    
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
    st.markdown("### 🎯 Staff Performance Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        staff_data = []
        for staff, data in stats['by_assignee'].items():
            staff_data.append({'Staff': staff, 'Ticket Count': data['count'], 'Avg Resolution (hrs)': data['avg_resolution']})
        staff_df = pd.DataFrame(staff_data) if staff_data else pd.DataFrame()
        
        if not staff_df.empty:
            fig = px.bar(staff_df, x='Staff', y='Ticket Count', title='Tickets Assigned by Staff', color='Ticket Count', color_continuous_scale='Blues')
            fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='white'), showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if not staff_df.empty:
            fig = px.bar(staff_df.sort_values('Avg Resolution (hrs)', ascending=True), y='Staff', x='Avg Resolution (hrs)', orientation='h', title='Avg Resolution Time by Staff (hours)', color='Avg Resolution (hrs)', color_continuous_scale='RdYlGn_r')
            fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='white'), showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
    
    if staff_data:
        worst_performer = max(staff_data, key=lambda x: x['Avg Resolution (hrs)'])
        best_performer = min(staff_data, key=lambda x: x['Avg Resolution (hrs)'])
        
        st.markdown(f"""
        <div style="padding: 20px; background: linear-gradient(145deg, rgba(157, 78, 221, 0.2), rgba(157, 78, 221, 0.1)); 
                    border-radius: 16px; border-left: 4px solid #9d4edd; margin: 20px 0;">
            <h4 style="color: #9d4edd; margin: 0 0 10px 0;">👥 Staff Performance Anomaly</h4>
            <p style="color: white; margin: 0;">
                <strong>{worst_performer['Staff']}</strong> has the longest avg resolution time at 
                <strong>{worst_performer['Avg Resolution (hrs)']} hours</strong>, vs 
                <strong>{best_performer['Staff']}</strong> at <strong>{best_performer['Avg Resolution (hrs)']} hours</strong>.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### ⏱️ Process Bottleneck Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        status_df = pd.DataFrame({'Status': list(stats['by_status'].keys()), 'Count': list(stats['by_status'].values())})
        colors = ['#f72585' if s == 'Waiting for User' else '#4361ee' for s in status_df['Status']]
        fig = px.bar(status_df, x='Status', y='Count', title='Tickets by Status', color='Status', color_discrete_sequence=colors)
        fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='white'), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        category_df = pd.DataFrame({'Category': list(stats['by_category'].keys()), 'Count': list(stats['by_category'].values())}).sort_values('Count', ascending=False)
        fig = px.pie(category_df, values='Count', names='Category', title='Tickets by Category', color_discrete_sequence=px.colors.sequential.Plasma_r, hole=0.4)
        fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='white'))
        st.plotly_chart(fig, use_container_width=True)
    
    waiting_count = stats['by_status'].get('Waiting for User', 0)
    if waiting_count > 0:
        st.markdown(f"""
        <div style="padding: 20px; background: linear-gradient(145deg, rgba(247, 37, 133, 0.2), rgba(247, 37, 133, 0.1)); 
                    border-radius: 16px; border-left: 4px solid #f72585; margin: 20px 0;">
            <h4 style="color: #f72585; margin: 0 0 10px 0;">⚠️ Process Bottleneck: "Waiting for User"</h4>
            <p style="color: white; margin: 0;">
                <strong>{waiting_count}</strong> tickets stuck in "Waiting for User" status. Consider automated follow-ups.
            </p>
        </div>
        """, unsafe_allow_html=True)


def render_explorer_tab(df: pd.DataFrame):
    """Render ticket explorer with filtering."""
    st.markdown("### 🔍 Ticket Explorer")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        status_filter = st.multiselect("Status", options=df['status'].unique().tolist(), default=df['status'].unique().tolist())
    with col2:
        priority_filter = st.multiselect("Priority", options=df['priority'].unique().tolist(), default=df['priority'].unique().tolist())
    with col3:
        category_filter = st.multiselect("Category", options=df['category'].unique().tolist(), default=df['category'].unique().tolist())
    with col4:
        search_term = st.text_input("Search", placeholder="Search tickets...")
    
    filtered_df = df[(df['status'].isin(status_filter)) & (df['priority'].isin(priority_filter)) & (df['category'].isin(category_filter))]
    
    if search_term:
        filtered_df = filtered_df[filtered_df['title'].str.contains(search_term, case=False, na=False) | filtered_df['description'].str.contains(search_term, case=False, na=False)]
    
    st.markdown(f"*Showing {len(filtered_df)} of {len(df)} tickets*")
    
    display_cols = ['ticket_id', 'title', 'category', 'priority', 'status', 'assigned_to', 'department', 'created_at', 'resolution_time_hours', 'sla_met']
    st.dataframe(filtered_df[display_cols].sort_values('created_at', ascending=False), use_container_width=True, height=400)


def render_crud_tab(db):
    """Render CRUD operations for tickets."""
    st.markdown("### ➕ Manage IT Tickets")
    
    action = st.radio("Select Action", ["Create New", "Update Existing", "Delete"], horizontal=True)
    
    if action == "Create New":
        with st.form("create_ticket_form"):
            st.markdown("#### Create New Ticket")
            col1, col2 = st.columns(2)
            with col1:
                new_id = st.text_input("Ticket ID", placeholder="e.g., TKT031")
                title = st.text_input("Title", placeholder="Brief issue description")
                category = st.selectbox("Category", ["Hardware", "Software", "Network", "Email", "Account"])
                priority = st.selectbox("Priority", ["Critical", "High", "Medium", "Low"])
            with col2:
                status = st.selectbox("Status", ["Open", "In Progress", "Waiting for User", "Resolved"])
                requester = st.text_input("Requester", placeholder="User name")
                department = st.text_input("Department", placeholder="e.g., Sales")
                assigned_to = st.selectbox("Assigned To", ["tech_support_01", "tech_support_02", "tech_support_03"])
            description = st.text_area("Description", placeholder="Detailed issue description")
            
            if st.form_submit_button("Create Ticket", use_container_width=True):
                if new_id and title and requester:
                    ticket_data = {'ticket_id': new_id, 'title': title, 'description': description, 'category': category, 'priority': priority, 'status': status, 'requester': requester, 'assigned_to': assigned_to, 'created_at': datetime.now().isoformat(), 'department': department}
                    if db.create_ticket(ticket_data):
                        st.success(f"✓ Ticket {new_id} created!")
                    else:
                        st.error("❌ Failed. ID may already exist.")
                else:
                    st.warning("⚠️ Please fill in required fields")
    
    elif action == "Update Existing":
        tickets = db.get_all_tickets()
        if tickets:
            ticket_ids = [tkt[0] for tkt in tickets]
            selected_id = st.selectbox("Select Ticket to Update", ticket_ids)
            
            if selected_id:
                ticket = db.get_ticket(selected_id)
                with st.form("update_ticket_form"):
                    st.markdown(f"#### Update Ticket: {selected_id}")
                    col1, col2 = st.columns(2)
                    with col1:
                        new_status = st.selectbox("Status", ["Open", "In Progress", "Waiting for User", "Resolved"], index=["Open", "In Progress", "Waiting for User", "Resolved"].index(ticket[5]) if ticket[5] in ["Open", "In Progress", "Waiting for User", "Resolved"] else 0)
                        new_priority = st.selectbox("Priority", ["Critical", "High", "Medium", "Low"], index=["Critical", "High", "Medium", "Low"].index(ticket[4]) if ticket[4] in ["Critical", "High", "Medium", "Low"] else 0)
                    with col2:
                        new_assigned = st.selectbox("Assigned To", ["tech_support_01", "tech_support_02", "tech_support_03"])
                        resolution_time = st.number_input("Resolution Time (hours)", value=float(ticket[11]) if ticket[11] else 0.0, min_value=0.0)
                        sla_met = st.selectbox("SLA Met", ["Yes", "No", "Pending"])
                        satisfaction = st.slider("Satisfaction Rating", 1, 5, int(ticket[14]) if ticket[14] else 3)
                    
                    if st.form_submit_button("Update Ticket", use_container_width=True):
                        updates = {'status': new_status, 'priority': new_priority, 'assigned_to': new_assigned}
                        if new_status == "Resolved":
                            updates['resolved_at'] = datetime.now().isoformat()
                            updates['resolution_time_hours'] = resolution_time
                            updates['sla_met'] = sla_met
                            updates['satisfaction_rating'] = satisfaction
                        if db.update_ticket(selected_id, **updates):
                            st.success(f"✓ Ticket {selected_id} updated!")
                            st.rerun()
                        else:
                            st.error("❌ Failed to update.")
    
    elif action == "Delete":
        tickets = db.get_all_tickets()
        if tickets:
            ticket_ids = [tkt[0] for tkt in tickets]
            selected_id = st.selectbox("Select Ticket to Delete", ticket_ids)
            
            if selected_id:
                st.warning(f"⚠️ Are you sure you want to delete ticket {selected_id}?")
                if st.button("🗑️ Delete Ticket", type="primary"):
                    if db.delete_ticket(selected_id):
                        st.success(f"✓ Ticket {selected_id} deleted!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to delete.")


def render_ai_tab(stats: dict):
    """Render AI Assistant tab with chatbox."""
    st.markdown("### 🤖 AI IT Operations Advisor")
    st.markdown("*Domain-restricted AI assistant for IT operations*")
    
    # Initialize chat history for this domain
    if 'it_chat' not in st.session_state:
        st.session_state.it_chat = []
    
    try:
        from ai_assistant import get_domain_assistant
        assistant = get_domain_assistant('it_operations')
        db = st.session_state.db
        
        if assistant is None or not assistant.is_configured():
            st.warning("""
            ⚠️ **AI Assistant Not Configured**
            
            To enable AI analysis:
            1. Get a Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey)
            2. Create a `.env` file with: `GEMINI_API_KEY_IT=your_key`
            3. Restart the application
            """)
            
            # Show demo chatbox even without API
            st.markdown("---")
            st.markdown("#### 💬 Chat Preview (Demo Mode)")
            _render_demo_chatbox("it")
            return
        
        st.info("🔒 This AI can ONLY answer IT operations questions.")
        
        # Quick analysis button
        if st.button("🔍 Auto-Analyze IT Performance", use_container_width=True):
            with st.spinner("Analyzing tickets..."):
                analysis = assistant.analyze_domain_data(db)
                st.session_state.it_chat.append({"role": "assistant", "content": f"**📊 Auto-Analysis Results:**\n\n{analysis}"})
                st.rerun()
        
        st.markdown("---")
        st.markdown("#### 💬 Chat with AI IT Advisor")
        
        # Chat container
        chat_container = st.container()
        
        with chat_container:
            # Display chat history
            for i, msg in enumerate(st.session_state.it_chat):
                if msg["role"] == "user":
                    st.markdown(f"""
                    <div style="background: rgba(102, 126, 234, 0.2); padding: 12px 16px; border-radius: 12px; margin: 8px 0; border-left: 3px solid #667eea;">
                        <strong style="color: #667eea;">🧑 You:</strong><br>
                        <span style="color: #ffffff;">{msg['content']}</span>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="background: rgba(157, 78, 221, 0.15); padding: 12px 16px; border-radius: 12px; margin: 8px 0; border-left: 3px solid #9d4edd;">
                        <strong style="color: #9d4edd;">🤖 AI:</strong><br>
                        <span style="color: #ffffff;">{msg['content']}</span>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Chat input
        st.markdown("---")
        col1, col2 = st.columns([5, 1])
        with col1:
            user_input = st.text_input(
                "Ask about IT tickets, SLA, or performance...",
                key="it_input",
                placeholder="e.g., Why is there a bottleneck in ticket resolution?",
                label_visibility="collapsed"
            )
        with col2:
            send_btn = st.button("Send", key="it_send", use_container_width=True)
        
        # Clear chat button
        col_a, col_b, col_c = st.columns([2, 1, 2])
        with col_b:
            if st.button("🗑️ Clear Chat", key="it_clear", use_container_width=True):
                st.session_state.it_chat = []
                st.rerun()
        
        # Process user input
        if send_btn and user_input:
            st.session_state.it_chat.append({"role": "user", "content": user_input})
            
            with st.spinner("🤖 Thinking..."):
                response = assistant.chat(user_input, db)
            
            st.session_state.it_chat.append({"role": "assistant", "content": response})
            st.rerun()
    
    except ImportError:
        st.info("AI Assistant module not available. Showing demo chatbox.")
        st.markdown("---")
        _render_demo_chatbox("it")


def _render_demo_chatbox(domain: str):
    """Render a demo chatbox when AI is not configured."""
    chat_key = f"{domain}_demo_chat"
    if chat_key not in st.session_state:
        st.session_state[chat_key] = []
    
    # Display demo messages
    for msg in st.session_state[chat_key]:
        role_color = "#667eea" if msg["role"] == "user" else "#9d4edd"
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
render_it_operations_page()
