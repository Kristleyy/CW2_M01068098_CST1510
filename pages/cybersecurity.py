"""
Cybersecurity Domain Dashboard
Addresses: Incident Response Bottleneck - Phishing surge analysis
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime


def render_cybersecurity_page():
    """Render the Cybersecurity dashboard."""
    st.markdown("# 🛡️ Cybersecurity Dashboard")
    st.markdown("*Incident Response & Threat Analysis*")
    
    # Get database instance
    db = st.session_state.db
    
    # Load incident data
    df = db.get_incidents_dataframe()
    
    if df.empty:
        st.warning("No incident data available. Please load sample data.")
        if st.button("Load Sample Data"):
            db.load_all_sample_data()
            st.rerun()
        return
    
    # Convert datetime columns
    df['created_at'] = pd.to_datetime(df['created_at'])
    df['resolved_at'] = pd.to_datetime(df['resolved_at'])
    
    # Get statistics
    stats = db.get_incident_stats()
    
    # ============== KEY METRICS ==============
    st.markdown("### 📈 Key Metrics")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            "Total Incidents",
            stats['total'],
            help="Total number of security incidents"
        )
    
    with col2:
        open_incidents = stats['by_status'].get('Open', 0) + stats['by_status'].get('In Progress', 0)
        st.metric(
            "Open/In Progress",
            open_incidents,
            delta=f"-{stats['by_status'].get('Resolved', 0)} resolved",
            delta_color="inverse"
        )
    
    with col3:
        critical_count = stats['by_severity'].get('Critical', 0)
        st.metric(
            "Critical Severity",
            critical_count,
            delta="Requires immediate attention" if critical_count > 0 else "All clear",
            delta_color="inverse" if critical_count > 0 else "normal"
        )
    
    with col4:
        phishing_count = stats['by_threat_type'].get('Phishing', 0)
        phishing_pct = round(phishing_count / stats['total'] * 100, 1) if stats['total'] > 0 else 0
        st.metric(
            "Phishing Incidents",
            phishing_count,
            delta=f"{phishing_pct}% of total",
            delta_color="inverse"
        )
    
    with col5:
        st.metric(
            "Avg Resolution Time",
            f"{stats['avg_resolution_hours']}h",
            help="Average time to resolve incidents"
        )
    
    st.markdown("---")
    
    # ============== TABS FOR DIFFERENT VIEWS ==============
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
    
    # ============== PHISHING SURGE ANALYSIS (Key Insight) ==============
    st.markdown("### 🎯 Critical Finding: Phishing Surge Analysis")
    
    # Phishing vs Other Threats
    col1, col2 = st.columns(2)
    
    with col1:
        # Threat type distribution
        threat_df = pd.DataFrame({
            'Threat Type': list(stats['by_threat_type'].keys()),
            'Count': list(stats['by_threat_type'].values())
        }).sort_values('Count', ascending=False)
        
        colors = ['#f72585' if t == 'Phishing' else '#4361ee' for t in threat_df['Threat Type']]
        
        fig = px.bar(
            threat_df,
            x='Threat Type',
            y='Count',
            title='Threat Type Distribution',
            color='Threat Type',
            color_discrete_sequence=colors
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Phishing incidents by status
        phishing_df = df[df['threat_type'] == 'Phishing']
        phishing_status = phishing_df['status'].value_counts()
        
        fig = px.pie(
            values=phishing_status.values,
            names=phishing_status.index,
            title='Phishing Incidents by Status',
            color_discrete_sequence=['#f72585', '#ffd166', '#06d6a0'],
            hole=0.4
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white')
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Key insight callout
    unresolved_phishing = len(phishing_df[phishing_df['status'] != 'Resolved'])
    st.markdown(f"""
    <div style="padding: 20px; background: linear-gradient(145deg, rgba(247, 37, 133, 0.2), rgba(247, 37, 133, 0.1)); 
                border-radius: 16px; border-left: 4px solid #f72585; margin: 20px 0;">
        <h4 style="color: #f72585; margin: 0 0 10px 0;">⚠️ Phishing Surge Detected</h4>
        <p style="color: white; margin: 0;">
            <strong>{stats['by_threat_type'].get('Phishing', 0)}</strong> phishing incidents identified, 
            representing <strong>{round(stats['by_threat_type'].get('Phishing', 0) / stats['total'] * 100, 1)}%</strong> of all incidents.
            <strong>{unresolved_phishing}</strong> remain unresolved, creating a significant response backlog.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ============== TIME SERIES ANALYSIS ==============
    st.markdown("### 📅 Incident Timeline")
    
    # Daily incident counts
    df['date'] = df['created_at'].dt.date
    daily_counts = df.groupby(['date', 'threat_type']).size().reset_index(name='count')
    
    fig = px.area(
        daily_counts,
        x='date',
        y='count',
        color='threat_type',
        title='Daily Incident Volume by Threat Type',
        color_discrete_map={'Phishing': '#f72585', 'Malware': '#4361ee', 'Unauthorized Access': '#06d6a0', 
                          'Data Breach': '#ffd166', 'Web Attack': '#4cc9f0', 'DDoS': '#9d4edd', 'Zero-Day': '#f94144'}
    )
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        xaxis_title="Date",
        yaxis_title="Number of Incidents"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # ============== RESOLUTION TIME ANALYSIS ==============
    st.markdown("### ⏱️ Resolution Time Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Resolution time by threat type
        resolved_df = df[df['resolved_at'].notna()].copy()
        if not resolved_df.empty:
            resolution_by_threat = resolved_df.groupby('threat_type')['resolution_time_hours'].mean().sort_values(ascending=True)
            
            fig = px.bar(
                x=resolution_by_threat.values,
                y=resolution_by_threat.index,
                orientation='h',
                title='Average Resolution Time by Threat Type (hours)',
                color=resolution_by_threat.values,
                color_continuous_scale='RdYlGn_r'
            )
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                showlegend=False,
                xaxis_title="Hours",
                yaxis_title=""
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Resolution time by severity
        if not resolved_df.empty:
            resolution_by_severity = resolved_df.groupby('severity')['resolution_time_hours'].mean()
            severity_order = ['Critical', 'High', 'Medium', 'Low']
            resolution_by_severity = resolution_by_severity.reindex([s for s in severity_order if s in resolution_by_severity.index])
            
            fig = px.bar(
                x=resolution_by_severity.index,
                y=resolution_by_severity.values,
                title='Average Resolution Time by Severity (hours)',
                color=resolution_by_severity.values,
                color_continuous_scale='RdYlGn_r'
            )
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                showlegend=False,
                xaxis_title="Severity",
                yaxis_title="Hours"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # ============== ANALYST WORKLOAD ==============
    st.markdown("### 👥 Analyst Workload & Performance")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Incidents by analyst
        analyst_counts = df['assigned_to'].value_counts()
        
        fig = px.bar(
            x=analyst_counts.index,
            y=analyst_counts.values,
            title='Incident Assignments by Analyst',
            color=analyst_counts.values,
            color_continuous_scale='Viridis'
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            showlegend=False,
            xaxis_title="Analyst",
            yaxis_title="Number of Incidents"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Resolution rate by analyst
        analyst_resolution = df.groupby('assigned_to').apply(
            lambda x: len(x[x['status'] == 'Resolved']) / len(x) * 100 if len(x) > 0 else 0
        ).sort_values(ascending=True)
        
        fig = px.bar(
            x=analyst_resolution.values,
            y=analyst_resolution.index,
            orientation='h',
            title='Resolution Rate by Analyst (%)',
            color=analyst_resolution.values,
            color_continuous_scale='RdYlGn'
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            showlegend=False,
            xaxis_title="Resolution Rate (%)",
            yaxis_title=""
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # ============== SEVERITY MATRIX ==============
    st.markdown("### 🎯 Severity vs Status Matrix")
    
    # Create heatmap data
    heatmap_data = pd.crosstab(df['severity'], df['status'])
    severity_order = ['Critical', 'High', 'Medium', 'Low']
    heatmap_data = heatmap_data.reindex([s for s in severity_order if s in heatmap_data.index])
    
    fig = px.imshow(
        heatmap_data.values,
        x=heatmap_data.columns.tolist(),
        y=heatmap_data.index.tolist(),
        color_continuous_scale='RdYlGn_r',
        aspect='auto',
        title='Incident Count: Severity vs Status'
    )
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    st.plotly_chart(fig, use_container_width=True)


def render_explorer_tab(df: pd.DataFrame):
    """Render incident explorer with filtering."""
    st.markdown("### 🔍 Incident Explorer")
    
    # Filters
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        status_filter = st.multiselect(
            "Status",
            options=df['status'].unique().tolist(),
            default=df['status'].unique().tolist()
        )
    
    with col2:
        severity_filter = st.multiselect(
            "Severity",
            options=df['severity'].unique().tolist(),
            default=df['severity'].unique().tolist()
        )
    
    with col3:
        threat_filter = st.multiselect(
            "Threat Type",
            options=df['threat_type'].unique().tolist(),
            default=df['threat_type'].unique().tolist()
        )
    
    with col4:
        search_term = st.text_input("Search", placeholder="Search incidents...")
    
    # Apply filters
    filtered_df = df[
        (df['status'].isin(status_filter)) &
        (df['severity'].isin(severity_filter)) &
        (df['threat_type'].isin(threat_filter))
    ]
    
    if search_term:
        filtered_df = filtered_df[
            filtered_df['title'].str.contains(search_term, case=False, na=False) |
            filtered_df['description'].str.contains(search_term, case=False, na=False)
        ]
    
    st.markdown(f"*Showing {len(filtered_df)} of {len(df)} incidents*")
    
    # Display table
    display_cols = ['incident_id', 'title', 'threat_type', 'severity', 'status', 'assigned_to', 'created_at', 'resolution_time_hours']
    st.dataframe(
        filtered_df[display_cols].sort_values('created_at', ascending=False),
        use_container_width=True,
        height=400
    )
    
    # Incident details
    st.markdown("### 📋 Incident Details")
    selected_incident = st.selectbox(
        "Select incident to view details",
        options=filtered_df['incident_id'].tolist(),
        format_func=lambda x: f"{x}: {filtered_df[filtered_df['incident_id']==x]['title'].values[0]}"
    )
    
    if selected_incident:
        incident = filtered_df[filtered_df['incident_id'] == selected_incident].iloc[0]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            **ID:** {incident['incident_id']}  
            **Title:** {incident['title']}  
            **Threat Type:** {incident['threat_type']}  
            **Severity:** {incident['severity']}  
            **Status:** {incident['status']}  
            """)
        
        with col2:
            st.markdown(f"""
            **Assigned To:** {incident['assigned_to']}  
            **Created:** {incident['created_at']}  
            **Source IP:** {incident['source_ip']}  
            **Target System:** {incident['target_system']}  
            **Resolution Time:** {incident['resolution_time_hours']} hours  
            """)
        
        st.markdown(f"**Description:** {incident['description']}")


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
                    incident_data = {
                        'incident_id': new_id,
                        'title': title,
                        'description': description,
                        'threat_type': threat_type,
                        'severity': severity,
                        'status': status,
                        'assigned_to': assigned_to,
                        'created_at': datetime.now().isoformat(),
                        'source_ip': source_ip,
                        'target_system': target_system
                    }
                    if db.create_incident(incident_data):
                        st.success(f"✓ Incident {new_id} created successfully!")
                    else:
                        st.error("❌ Failed to create incident. ID may already exist.")
                else:
                    st.warning("⚠️ Please fill in required fields (ID, Title, Assigned To)")
    
    elif action == "Update Existing":
        incidents = db.get_all_incidents()
        incident_ids = [inc[0] for inc in incidents]
        
        selected_id = st.selectbox("Select Incident to Update", incident_ids)
        
        if selected_id:
            incident = db.get_incident(selected_id)
            
            with st.form("update_incident_form"):
                st.markdown(f"#### Update Incident: {selected_id}")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    new_status = st.selectbox("Status", ["Open", "In Progress", "Resolved"], 
                                             index=["Open", "In Progress", "Resolved"].index(incident[5]) if incident[5] in ["Open", "In Progress", "Resolved"] else 0)
                    new_severity = st.selectbox("Severity", ["Critical", "High", "Medium", "Low"],
                                               index=["Critical", "High", "Medium", "Low"].index(incident[4]) if incident[4] in ["Critical", "High", "Medium", "Low"] else 0)
                
                with col2:
                    new_assigned = st.text_input("Assigned To", value=incident[6] or "")
                    resolution_time = st.number_input("Resolution Time (hours)", value=incident[9] or 0.0, min_value=0.0)
                
                if st.form_submit_button("Update Incident", use_container_width=True):
                    updates = {
                        'status': new_status,
                        'severity': new_severity,
                        'assigned_to': new_assigned
                    }
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
    """Render AI Assistant tab for Cybersecurity domain."""
    st.markdown("### 🤖 AI Security Analyst")
    st.markdown("*Domain-restricted AI assistant for cybersecurity analysis only*")
    
    # Import domain-specific AI assistant
    try:
        from ai_assistant import get_domain_assistant
        assistant = get_domain_assistant('cybersecurity')
        db = st.session_state.db
        
        if assistant is None or not assistant.is_configured():
            st.warning("""
            ⚠️ **Cybersecurity AI Assistant Not Configured**
            
            To enable this AI assistant, please:
            1. Get a Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey)
            2. Create a `.env` file in the project root
            3. Add: `GEMINI_API_KEY_CYBER=your_api_key_here`
            4. Restart the application
            
            **Note:** Each domain requires its own separate API key for security isolation.
            """)
            return
        
        # Domain restriction notice
        st.info("🔒 This AI assistant can ONLY answer questions about cybersecurity topics. It has access to security incident data only.")
        
        # Quick analysis button
        if st.button("🔍 Analyze Security Incidents", use_container_width=True):
            with st.spinner("Analyzing incidents..."):
                analysis = assistant.analyze_domain_data(db)
                st.markdown("#### Analysis Results")
                st.markdown(analysis)
        
        st.markdown("---")
        
        # Chat interface
        st.markdown("#### Ask the Security AI")
        
        # Chat history
        if 'cyber_chat' not in st.session_state:
            st.session_state.cyber_chat = []
        
        # Display chat history in a container
        chat_container = st.container()
        with chat_container:
            for msg in st.session_state.cyber_chat:
                if msg["role"] == "user":
                    st.markdown(f"**🧑 You:** {msg['content']}")
                else:
                    st.markdown(f"**🤖 AI:** {msg['content']}")
                st.markdown("---")
        
        # Chat input using text_input (works inside tabs)
        col1, col2 = st.columns([5, 1])
        with col1:
            prompt = st.text_input("Ask about security incidents, threats, or best practices...", 
                                   key="cyber_input", label_visibility="collapsed",
                                   placeholder="Ask about security incidents, threats, or best practices...")
        with col2:
            send_btn = st.button("Send", key="cyber_send", use_container_width=True)
        
        if send_btn and prompt:
            # Add user message
            st.session_state.cyber_chat.append({"role": "user", "content": prompt})
            
            # Get AI response (with domain-specific data access)
            with st.spinner("Thinking..."):
                response = assistant.chat(prompt, db)
            
            st.session_state.cyber_chat.append({"role": "assistant", "content": response})
            st.rerun()
    
    except ImportError:
        st.error("AI Assistant module not found. Please ensure ai_assistant.py is in the project directory.")

