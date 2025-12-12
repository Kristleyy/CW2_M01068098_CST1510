"""
Data Science Domain Dashboard
Addresses: Data Governance & Discovery - Resource consumption and data source dependency analysis
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Page configuration - MUST be first Streamlit command
st.set_page_config(
    page_title="Data Science - MDIP",
    page_icon="📊",
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
        border-right: 1px solid rgba(0, 212, 255, 0.3);
    }
    
    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }
    
    [data-testid="stMetric"] {
        background: linear-gradient(145deg, #2d2d44, #1e1e2e);
        border: 1px solid rgba(0, 212, 255, 0.3);
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
    
    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        font-family: 'JetBrains Mono', monospace !important;
        color: #00d4ff !important;
    }
    
    .stButton > button {
        font-family: 'Outfit', sans-serif;
        background: linear-gradient(135deg, #00d4ff 0%, #0077b6 100%);
        color: white !important;
        border: none;
        border-radius: 12px;
        padding: 12px 28px;
        font-weight: 500;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0, 212, 255, 0.4);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 212, 255, 0.6);
    }
    
    .stTextInput > div > div > input, .stSelectbox > div > div, .stMultiSelect > div > div, .stTextArea textarea {
        background: rgba(45, 45, 68, 0.9) !important;
        border: 1px solid rgba(0, 212, 255, 0.4);
        border-radius: 12px;
        color: #ffffff !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: rgba(45, 45, 68, 0.8);
        border-radius: 10px;
        color: #e0e0e0 !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(0, 212, 255, 0.4), rgba(0, 119, 182, 0.4));
        color: #ffffff !important;
        border: 1px solid rgba(0, 212, 255, 0.5);
    }
    
    .stDataFrame { border-radius: 12px; overflow: hidden; }
    
    .stSuccess { background-color: rgba(6, 214, 160, 0.2) !important; border-radius: 12px; }
    .stError { background-color: rgba(247, 37, 133, 0.2) !important; border-radius: 12px; }
    .stWarning { background-color: rgba(255, 209, 102, 0.2) !important; border-radius: 12px; }
    .stInfo { background-color: rgba(0, 212, 255, 0.2) !important; border-radius: 12px; }
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
    allowed_roles = ['datascience', 'admin']
    
    if user_role not in allowed_roles:
        st.error(f"⛔ Access Denied. Your role ({user_role}) does not have permission to access the Data Science dashboard.")
        st.stop()


def render_sidebar():
    """Render the sidebar with user info and logout."""
    with st.sidebar:
        st.markdown("""
        <div style="padding: 20px 0; text-align: center;">
            <h2 style="margin: 0; color: #00d4ff;">📊 Data Science</h2>
            <p style="color: #e0e0e0; font-size: 0.9rem;">Data Governance Platform</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        user = st.session_state.user
        st.markdown(f"""
        <div style="padding: 15px; background: rgba(0, 212, 255, 0.1); border-radius: 12px; margin-bottom: 20px; border: 1px solid rgba(0, 212, 255, 0.3);">
            <p style="margin: 0; font-size: 0.9rem; color: #e0e0e0;">Logged in as</p>
            <p style="margin: 5px 0; font-size: 1.1rem; font-weight: 600; color: #ffffff;">📊 {user.get('username', 'User')}</p>
            <p style="margin: 0; font-size: 0.85rem; color: #00d4ff;">Data Scientist</p>
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


def render_datascience_page():
    """Render the Data Science dashboard."""
    st.markdown("# 📊 Data Science Dashboard")
    st.markdown("*Data Governance & Discovery Platform*")
    
    db = st.session_state.db
    df = db.get_datasets_dataframe()
    
    if df.empty:
        st.warning("No dataset metadata available. Please load sample data.")
        if st.button("Load Sample Data"):
            db.load_all_sample_data("DATA")
            st.rerun()
        return
    
    df['upload_date'] = pd.to_datetime(df['upload_date'])
    df['last_accessed'] = pd.to_datetime(df['last_accessed'])
    
    stats = db.get_dataset_stats()
    
    # KEY METRICS
    st.markdown("### 📈 Key Metrics")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Datasets", stats['total'])
    with col2:
        st.metric("Total Storage", f"{stats['total_size_gb']} GB")
    with col3:
        active_count = stats['by_status'].get('Active', 0)
        st.metric("Active Datasets", active_count, delta=f"{round(active_count/stats['total']*100, 1)}% of total" if stats['total'] > 0 else "0%")
    with col4:
        deprecated_count = stats['by_status'].get('Deprecated', 0)
        st.metric("Deprecated", deprecated_count, delta="Needs review" if deprecated_count > 0 else "Clean", delta_color="inverse" if deprecated_count > 0 else "normal")
    with col5:
        st.metric("Avg Quality Score", f"{stats['avg_quality_score']}%")
    
    st.markdown("---")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Analytics", "🔍 Dataset Explorer", "➕ Manage Datasets", "🤖 AI Assistant"])
    
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
    st.markdown("### 🎯 Resource Consumption Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        dept_data = []
        for dept, data in stats['by_department'].items():
            dept_data.append({'Department': dept, 'Size (GB)': round(data['size_mb'] / 1024, 2), 'Dataset Count': data['count']})
        dept_df = pd.DataFrame(dept_data).sort_values('Size (GB)', ascending=False) if dept_data else pd.DataFrame()
        
        if not dept_df.empty:
            fig = px.bar(dept_df, x='Department', y='Size (GB)', title='Storage Consumption by Department', color='Size (GB)', color_continuous_scale='Blues')
            fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='white'), showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if not dept_df.empty:
            fig = px.pie(dept_df, values='Dataset Count', names='Department', title='Dataset Distribution by Department', color_discrete_sequence=px.colors.sequential.Plasma_r, hole=0.4)
            fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='white'))
            st.plotly_chart(fig, use_container_width=True)
    
    if dept_data:
        top_dept = dept_df.iloc[0]
        st.markdown(f"""
        <div style="padding: 20px; background: linear-gradient(145deg, rgba(0, 212, 255, 0.2), rgba(0, 212, 255, 0.1)); 
                    border-radius: 16px; border-left: 4px solid #00d4ff; margin: 20px 0;">
            <h4 style="color: #00d4ff; margin: 0 0 10px 0;">📊 Top Resource Consumer: {top_dept['Department']}</h4>
            <p style="color: white; margin: 0;">
                The <strong>{top_dept['Department']}</strong> department consumes <strong>{top_dept['Size (GB)']} GB</strong> 
                across <strong>{top_dept['Dataset Count']}</strong> datasets.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### ✅ Data Quality Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        quality_by_dept = df.groupby('source_department')['quality_score'].mean().sort_values(ascending=True)
        fig = px.bar(x=quality_by_dept.values, y=quality_by_dept.index, orientation='h', title='Average Quality Score by Department', color=quality_by_dept.values, color_continuous_scale='RdYlGn')
        fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='white'), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.scatter(df, x='size_mb', y='quality_score', color='source_department', size='row_count', title='Quality Score vs Size', hover_data=['name'])
        fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='white'))
        st.plotly_chart(fig, use_container_width=True)


def render_explorer_tab(df: pd.DataFrame):
    """Render dataset explorer with filtering."""
    st.markdown("### 🔍 Dataset Explorer")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        dept_filter = st.multiselect("Department", options=df['source_department'].unique().tolist(), default=df['source_department'].unique().tolist())
    with col2:
        status_filter = st.multiselect("Status", options=df['status'].unique().tolist(), default=df['status'].unique().tolist())
    with col3:
        format_filter = st.multiselect("Format", options=df['file_format'].unique().tolist(), default=df['file_format'].unique().tolist())
    with col4:
        search_term = st.text_input("Search", placeholder="Search datasets...")
    
    filtered_df = df[(df['source_department'].isin(dept_filter)) & (df['status'].isin(status_filter)) & (df['file_format'].isin(format_filter))]
    
    if search_term:
        filtered_df = filtered_df[filtered_df['name'].str.contains(search_term, case=False, na=False) | filtered_df['description'].str.contains(search_term, case=False, na=False)]
    
    st.markdown(f"*Showing {len(filtered_df)} of {len(df)} datasets*")
    
    display_cols = ['dataset_id', 'name', 'source_department', 'file_format', 'size_mb', 'row_count', 'quality_score', 'status', 'upload_date']
    st.dataframe(filtered_df[display_cols].sort_values('upload_date', ascending=False), use_container_width=True, height=400)


def render_crud_tab(db):
    """Render CRUD operations for datasets."""
    st.markdown("### ➕ Manage Datasets")
    
    action = st.radio("Select Action", ["Register New", "Update Existing", "Delete"], horizontal=True)
    
    if action == "Register New":
        with st.form("create_dataset_form"):
            st.markdown("#### Register New Dataset")
            col1, col2 = st.columns(2)
            with col1:
                new_id = st.text_input("Dataset ID", placeholder="e.g., DS021")
                name = st.text_input("Name", placeholder="Dataset name")
                source_dept = st.selectbox("Source Department", ["IT", "Cybersecurity", "Finance", "Marketing", "HR", "Operations", "Sales", "Legal", "Engineering"])
                file_format = st.selectbox("File Format", ["CSV", "JSON", "Parquet", "XLSX", "XML", "PDF"])
            with col2:
                size_mb = st.number_input("Size (MB)", min_value=0.0, value=0.0)
                row_count = st.number_input("Row Count", min_value=0, value=0)
                column_count = st.number_input("Column Count", min_value=0, value=0)
                quality_score = st.slider("Quality Score", 0.0, 100.0, 80.0)
            description = st.text_area("Description", placeholder="Dataset description")
            uploaded_by = st.text_input("Uploaded By", placeholder="username")
            
            if st.form_submit_button("Register Dataset", use_container_width=True):
                if new_id and name and uploaded_by:
                    dataset_data = {'dataset_id': new_id, 'name': name, 'description': description, 'source_department': source_dept, 'file_format': file_format, 'size_mb': size_mb, 'row_count': row_count, 'column_count': column_count, 'uploaded_by': uploaded_by, 'upload_date': datetime.now().isoformat(), 'last_accessed': datetime.now().isoformat(), 'quality_score': quality_score, 'status': 'Active', 'storage_location': f'/data/{source_dept.lower()}/{new_id}'}
                    if db.create_dataset(dataset_data):
                        st.success(f"✓ Dataset {new_id} registered!")
                    else:
                        st.error("❌ Failed. ID may already exist.")
                else:
                    st.warning("⚠️ Please fill in required fields")
    
    elif action == "Update Existing":
        datasets = db.get_all_datasets()
        if datasets:
            dataset_ids = [ds[0] for ds in datasets]
            selected_id = st.selectbox("Select Dataset to Update", dataset_ids)
            
            if selected_id:
                dataset = db.get_dataset(selected_id)
                with st.form("update_dataset_form"):
                    st.markdown(f"#### Update Dataset: {selected_id}")
                    col1, col2 = st.columns(2)
                    with col1:
                        new_status = st.selectbox("Status", ["Active", "Archived", "Deprecated"], index=["Active", "Archived", "Deprecated"].index(dataset[12]) if dataset[12] in ["Active", "Archived", "Deprecated"] else 0)
                        new_quality = st.slider("Quality Score", 0.0, 100.0, float(dataset[11]) if dataset[11] else 80.0)
                    with col2:
                        new_size = st.number_input("Size (MB)", value=float(dataset[5]) if dataset[5] else 0.0, min_value=0.0)
                        new_rows = st.number_input("Row Count", value=int(dataset[6]) if dataset[6] else 0, min_value=0)
                    
                    if st.form_submit_button("Update Dataset", use_container_width=True):
                        updates = {'status': new_status, 'quality_score': new_quality, 'size_mb': new_size, 'row_count': new_rows, 'last_accessed': datetime.now().isoformat()}
                        if db.update_dataset(selected_id, **updates):
                            st.success(f"✓ Dataset {selected_id} updated!")
                            st.rerun()
                        else:
                            st.error("❌ Failed to update.")
    
    elif action == "Delete":
        datasets = db.get_all_datasets()
        if datasets:
            dataset_ids = [ds[0] for ds in datasets]
            selected_id = st.selectbox("Select Dataset to Delete", dataset_ids)
            
            if selected_id:
                st.warning(f"⚠️ Are you sure you want to delete dataset {selected_id}?")
                if st.button("🗑️ Delete Dataset", type="primary"):
                    if db.delete_dataset(selected_id):
                        st.success(f"✓ Dataset {selected_id} deleted!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to delete.")


def render_ai_tab(stats: dict):
    """Render AI Assistant tab with chatbox."""
    st.markdown("### 🤖 AI Data Governance Advisor")
    st.markdown("*Domain-restricted AI assistant for data science*")
    
    # Initialize chat history for this domain
    if 'ds_chat' not in st.session_state:
        st.session_state.ds_chat = []
    
    try:
        from ai_assistant import get_domain_assistant
        assistant = get_domain_assistant('datascience')
        db = st.session_state.db
        
        if assistant is None or not assistant.is_configured():
            st.warning("""
            ⚠️ **AI Assistant Not Configured**
            
            To enable AI analysis:
            1. Get a Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey)
            2. Create a `.env` file with: `GEMINI_API_KEY_DATA=your_key`
            3. Restart the application
            """)
            
            # Show demo chatbox even without API
            st.markdown("---")
            st.markdown("#### 💬 Chat Preview (Demo Mode)")
            _render_demo_chatbox("ds")
            return
        
        st.info("🔒 This AI can ONLY answer data science questions.")
        
        # Quick analysis button
        if st.button("🔍 Auto-Analyze Data Governance", use_container_width=True):
            with st.spinner("Analyzing datasets..."):
                analysis = assistant.analyze_domain_data(db)
                st.session_state.ds_chat.append({"role": "assistant", "content": f"**📊 Auto-Analysis Results:**\n\n{analysis}"})
                st.rerun()
        
        st.markdown("---")
        st.markdown("#### 💬 Chat with AI Data Advisor")
        
        # Chat container
        chat_container = st.container()
        
        with chat_container:
            # Display chat history
            for i, msg in enumerate(st.session_state.ds_chat):
                if msg["role"] == "user":
                    st.markdown(f"""
                    <div style="background: rgba(102, 126, 234, 0.2); padding: 12px 16px; border-radius: 12px; margin: 8px 0; border-left: 3px solid #667eea;">
                        <strong style="color: #667eea;">🧑 You:</strong><br>
                        <span style="color: #ffffff;">{msg['content']}</span>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="background: rgba(0, 212, 255, 0.15); padding: 12px 16px; border-radius: 12px; margin: 8px 0; border-left: 3px solid #00d4ff;">
                        <strong style="color: #00d4ff;">🤖 AI:</strong><br>
                        <span style="color: #ffffff;">{msg['content']}</span>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Chat input
        st.markdown("---")
        col1, col2 = st.columns([5, 1])
        with col1:
            user_input = st.text_input(
                "Ask about data governance, quality, or archiving...",
                key="ds_input",
                placeholder="e.g., Which datasets should be archived?",
                label_visibility="collapsed"
            )
        with col2:
            send_btn = st.button("Send", key="ds_send", use_container_width=True)
        
        # Clear chat button
        col_a, col_b, col_c = st.columns([2, 1, 2])
        with col_b:
            if st.button("🗑️ Clear Chat", key="ds_clear", use_container_width=True):
                st.session_state.ds_chat = []
                st.rerun()
        
        # Process user input
        if send_btn and user_input:
            st.session_state.ds_chat.append({"role": "user", "content": user_input})
            
            with st.spinner("🤖 Thinking..."):
                response = assistant.chat(user_input, db)
            
            st.session_state.ds_chat.append({"role": "assistant", "content": response})
            st.rerun()
    
    except ImportError:
        st.info("AI Assistant module not available. Showing demo chatbox.")
        st.markdown("---")
        _render_demo_chatbox("ds")


def _render_demo_chatbox(domain: str):
    """Render a demo chatbox when AI is not configured."""
    chat_key = f"{domain}_demo_chat"
    if chat_key not in st.session_state:
        st.session_state[chat_key] = []
    
    # Display demo messages
    for msg in st.session_state[chat_key]:
        role_color = "#667eea" if msg["role"] == "user" else "#00d4ff"
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
render_datascience_page()
