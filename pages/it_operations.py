"""
IT Operations Domain Dashboard
Addresses: Service Desk Performance - Staff performance anomaly and process inefficiency analysis
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta


def render_it_operations_page():
    """Render the IT Operations dashboard."""
    st.markdown("# 🖥️ IT Operations Dashboard")
    st.markdown("*Service Desk Performance & Optimization*")
    
    # Get database instance
    db = st.session_state.db
    
    # Load ticket data
    df = db.get_tickets_dataframe()
    
    if df.empty:
        st.warning("No ticket data available. Please load sample data.")
        if st.button("Load Sample Data"):
            db.load_all_sample_data()
            st.rerun()
        return
    
    # Convert datetime columns
    df['created_at'] = pd.to_datetime(df['created_at'])
    df['first_response_at'] = pd.to_datetime(df['first_response_at'])
    df['resolved_at'] = pd.to_datetime(df['resolved_at'])
    
    # Get statistics
    stats = db.get_ticket_stats()
    
    # ============== KEY METRICS ==============
    st.markdown("### 📈 Key Metrics")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            "Total Tickets",
            stats['total'],
            help="Total IT support tickets"
        )
    
    with col2:
        open_tickets = stats['by_status'].get('In Progress', 0) + stats['by_status'].get('Waiting for User', 0)
        st.metric(
            "Open Tickets",
            open_tickets,
            delta=f"{stats['by_status'].get('Resolved', 0)} resolved",
            delta_color="off"
        )
    
    with col3:
        waiting_count = stats['by_status'].get('Waiting for User', 0)
        st.metric(
            "Waiting for User",
            waiting_count,
            delta="Process bottleneck" if waiting_count > 3 else "Normal",
            delta_color="inverse" if waiting_count > 3 else "normal"
        )
    
    with col4:
        st.metric(
            "SLA Compliance",
            f"{stats['sla_compliance']}%",
            delta="Target: 95%",
            delta_color="normal" if stats['sla_compliance'] >= 95 else "inverse"
        )
    
    with col5:
        st.metric(
            "Avg Resolution",
            f"{stats['avg_resolution_hours']}h",
            help="Average ticket resolution time"
        )
    
    st.markdown("---")
    
    # ============== TABS ==============
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
    
    # ============== STAFF PERFORMANCE ANALYSIS (Key Insight) ==============
    st.markdown("### 🎯 Staff Performance Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Tickets per staff member
        staff_data = []
        for staff, data in stats['by_assignee'].items():
            staff_data.append({
                'Staff': staff,
                'Ticket Count': data['count'],
                'Avg Resolution (hrs)': data['avg_resolution']
            })
        staff_df = pd.DataFrame(staff_data)
        
        fig = px.bar(
            staff_df,
            x='Staff',
            y='Ticket Count',
            title='Tickets Assigned by Staff Member',
            color='Ticket Count',
            color_continuous_scale='Blues'
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Average resolution time by staff
        fig = px.bar(
            staff_df.sort_values('Avg Resolution (hrs)', ascending=True),
            y='Staff',
            x='Avg Resolution (hrs)',
            orientation='h',
            title='Average Resolution Time by Staff (hours)',
            color='Avg Resolution (hrs)',
            color_continuous_scale='RdYlGn_r'
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Identify performance anomaly
    if staff_data:
        worst_performer = max(staff_data, key=lambda x: x['Avg Resolution (hrs)'])
        best_performer = min(staff_data, key=lambda x: x['Avg Resolution (hrs)'])
        
        st.markdown(f"""
        <div style="padding: 20px; background: linear-gradient(145deg, rgba(157, 78, 221, 0.2), rgba(157, 78, 221, 0.1)); 
                    border-radius: 16px; border-left: 4px solid #9d4edd; margin: 20px 0;">
            <h4 style="color: #9d4edd; margin: 0 0 10px 0;">👥 Staff Performance Anomaly Detected</h4>
            <p style="color: white; margin: 0;">
                <strong>{worst_performer['Staff']}</strong> has the longest average resolution time at 
                <strong>{worst_performer['Avg Resolution (hrs)']} hours</strong>, compared to 
                <strong>{best_performer['Staff']}</strong> at <strong>{best_performer['Avg Resolution (hrs)']} hours</strong>.
                This represents a <strong>{round((worst_performer['Avg Resolution (hrs)'] - best_performer['Avg Resolution (hrs)']) / best_performer['Avg Resolution (hrs)'] * 100, 1) if best_performer['Avg Resolution (hrs)'] > 0 else 0}%</strong> performance gap.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ============== PROCESS BOTTLENECK ANALYSIS ==============
    st.markdown("### ⏱️ Process Bottleneck Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Status distribution
        status_df = pd.DataFrame({
            'Status': list(stats['by_status'].keys()),
            'Count': list(stats['by_status'].values())
        })
        
        # Highlight "Waiting for User" as bottleneck
        colors = ['#f72585' if s == 'Waiting for User' else '#4361ee' for s in status_df['Status']]
        
        fig = px.bar(
            status_df,
            x='Status',
            y='Count',
            title='Tickets by Status',
            color='Status',
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
        # Average time in each status (calculate from open tickets)
        waiting_tickets = df[df['status'] == 'Waiting for User']
        if not waiting_tickets.empty:
            waiting_tickets = waiting_tickets.copy()
            waiting_tickets['wait_hours'] = (datetime.now() - waiting_tickets['created_at']).dt.total_seconds() / 3600
            avg_wait = waiting_tickets['wait_hours'].mean()
            
            status_times = {
                'Resolved': stats['avg_resolution_hours'],
                'In Progress': avg_wait * 0.3,  # Estimate
                'Waiting for User': avg_wait
            }
            
            fig = px.bar(
                x=list(status_times.keys()),
                y=list(status_times.values()),
                title='Average Time in Status (hours)',
                color=list(status_times.values()),
                color_continuous_scale='RdYlGn_r'
            )
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                showlegend=False,
                xaxis_title="Status",
                yaxis_title="Hours"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Bottleneck callout
    waiting_count = stats['by_status'].get('Waiting for User', 0)
    if waiting_count > 0:
        st.markdown(f"""
        <div style="padding: 20px; background: linear-gradient(145deg, rgba(247, 37, 133, 0.2), rgba(247, 37, 133, 0.1)); 
                    border-radius: 16px; border-left: 4px solid #f72585; margin: 20px 0;">
            <h4 style="color: #f72585; margin: 0 0 10px 0;">⚠️ Process Bottleneck: "Waiting for User" Status</h4>
            <p style="color: white; margin: 0;">
                <strong>{waiting_count}</strong> tickets are stuck in "Waiting for User" status, causing significant delays.
                This status is the greatest contributor to slow resolution times. Consider implementing automated follow-ups
                or clearer user communication protocols.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ============== CATEGORY ANALYSIS ==============
    st.markdown("### 📂 Ticket Category Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Category distribution
        category_df = pd.DataFrame({
            'Category': list(stats['by_category'].keys()),
            'Count': list(stats['by_category'].values())
        }).sort_values('Count', ascending=False)
        
        fig = px.pie(
            category_df,
            values='Count',
            names='Category',
            title='Tickets by Category',
            color_discrete_sequence=px.colors.sequential.Plasma_r,
            hole=0.4
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white')
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Resolution time by category
        resolved_df = df[df['resolved_at'].notna()].copy()
        if not resolved_df.empty:
            resolution_by_cat = resolved_df.groupby('category')['resolution_time_hours'].mean().sort_values(ascending=True)
            
            fig = px.bar(
                x=resolution_by_cat.values,
                y=resolution_by_cat.index,
                orientation='h',
                title='Avg Resolution Time by Category (hours)',
                color=resolution_by_cat.values,
                color_continuous_scale='RdYlGn_r'
            )
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # ============== SLA COMPLIANCE ==============
    st.markdown("### ✅ SLA Compliance Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # SLA compliance pie
        sla_df = df[df['sla_met'].notna()]
        sla_counts = sla_df['sla_met'].value_counts()
        
        fig = px.pie(
            values=sla_counts.values,
            names=['SLA Met' if x == 'Yes' else 'SLA Missed' for x in sla_counts.index],
            title='SLA Compliance Rate',
            color_discrete_sequence=['#06d6a0', '#f72585'],
            hole=0.4
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white')
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # SLA by priority
        sla_by_priority = sla_df.groupby('priority').apply(
            lambda x: (x['sla_met'] == 'Yes').sum() / len(x) * 100 if len(x) > 0 else 0
        )
        priority_order = ['Critical', 'High', 'Medium', 'Low']
        sla_by_priority = sla_by_priority.reindex([p for p in priority_order if p in sla_by_priority.index])
        
        fig = px.bar(
            x=sla_by_priority.index,
            y=sla_by_priority.values,
            title='SLA Compliance by Priority (%)',
            color=sla_by_priority.values,
            color_continuous_scale='RdYlGn'
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            showlegend=False,
            xaxis_title="Priority",
            yaxis_title="SLA Met (%)"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # ============== SATISFACTION ANALYSIS ==============
    st.markdown("### ⭐ Customer Satisfaction")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Satisfaction distribution
        sat_df = df[df['satisfaction_rating'].notna()]
        if not sat_df.empty:
            sat_counts = sat_df['satisfaction_rating'].value_counts().sort_index()
            
            fig = px.bar(
                x=sat_counts.index,
                y=sat_counts.values,
                title='Satisfaction Rating Distribution',
                color=sat_counts.index,
                color_continuous_scale='RdYlGn'
            )
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                showlegend=False,
                xaxis_title="Rating (1-5)",
                yaxis_title="Count"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Average satisfaction by staff
        if not sat_df.empty:
            sat_by_staff = sat_df.groupby('assigned_to')['satisfaction_rating'].mean().sort_values(ascending=True)
            
            fig = px.bar(
                x=sat_by_staff.values,
                y=sat_by_staff.index,
                orientation='h',
                title='Avg Satisfaction by Staff Member',
                color=sat_by_staff.values,
                color_continuous_scale='RdYlGn'
            )
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                showlegend=False,
                xaxis_title="Rating (1-5)",
                yaxis_title=""
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # ============== TIMELINE ==============
    st.markdown("### 📅 Ticket Timeline")
    
    df['date'] = df['created_at'].dt.date
    daily_counts = df.groupby(['date', 'priority']).size().reset_index(name='count')
    
    fig = px.area(
        daily_counts,
        x='date',
        y='count',
        color='priority',
        title='Daily Ticket Volume by Priority',
        color_discrete_map={'Critical': '#f72585', 'High': '#f77f00', 'Medium': '#ffd166', 'Low': '#06d6a0'}
    )
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        xaxis_title="Date",
        yaxis_title="Tickets"
    )
    st.plotly_chart(fig, use_container_width=True)


def render_explorer_tab(df: pd.DataFrame):
    """Render ticket explorer with filtering."""
    st.markdown("### 🔍 Ticket Explorer")
    
    # Filters
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        status_filter = st.multiselect(
            "Status",
            options=df['status'].unique().tolist(),
            default=df['status'].unique().tolist()
        )
    
    with col2:
        priority_filter = st.multiselect(
            "Priority",
            options=df['priority'].unique().tolist(),
            default=df['priority'].unique().tolist()
        )
    
    with col3:
        category_filter = st.multiselect(
            "Category",
            options=df['category'].unique().tolist(),
            default=df['category'].unique().tolist()
        )
    
    with col4:
        search_term = st.text_input("Search", placeholder="Search tickets...")
    
    # Apply filters
    filtered_df = df[
        (df['status'].isin(status_filter)) &
        (df['priority'].isin(priority_filter)) &
        (df['category'].isin(category_filter))
    ]
    
    if search_term:
        filtered_df = filtered_df[
            filtered_df['title'].str.contains(search_term, case=False, na=False) |
            filtered_df['description'].str.contains(search_term, case=False, na=False)
        ]
    
    st.markdown(f"*Showing {len(filtered_df)} of {len(df)} tickets*")
    
    # Display table
    display_cols = ['ticket_id', 'title', 'category', 'priority', 'status', 'assigned_to', 'department', 'created_at', 'resolution_time_hours', 'sla_met']
    st.dataframe(
        filtered_df[display_cols].sort_values('created_at', ascending=False),
        use_container_width=True,
        height=400
    )
    
    # Ticket details
    st.markdown("### 📋 Ticket Details")
    selected_ticket = st.selectbox(
        "Select ticket to view details",
        options=filtered_df['ticket_id'].tolist(),
        format_func=lambda x: f"{x}: {filtered_df[filtered_df['ticket_id']==x]['title'].values[0]}"
    )
    
    if selected_ticket:
        ticket = filtered_df[filtered_df['ticket_id'] == selected_ticket].iloc[0]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            **ID:** {ticket['ticket_id']}  
            **Title:** {ticket['title']}  
            **Category:** {ticket['category']}  
            **Priority:** {ticket['priority']}  
            **Status:** {ticket['status']}  
            """)
        
        with col2:
            st.markdown(f"""
            **Requester:** {ticket['requester']}  
            **Department:** {ticket['department']}  
            **Assigned To:** {ticket['assigned_to']}  
            **Created:** {ticket['created_at']}  
            """)
        
        with col3:
            st.markdown(f"""
            **First Response:** {ticket['first_response_at']}  
            **Resolved:** {ticket['resolved_at']}  
            **Resolution Time:** {ticket['resolution_time_hours']} hours  
            **SLA Met:** {ticket['sla_met']}  
            **Satisfaction:** {ticket['satisfaction_rating']}/5  
            """)
        
        st.markdown(f"**Description:** {ticket['description']}")


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
                    ticket_data = {
                        'ticket_id': new_id,
                        'title': title,
                        'description': description,
                        'category': category,
                        'priority': priority,
                        'status': status,
                        'requester': requester,
                        'assigned_to': assigned_to,
                        'created_at': datetime.now().isoformat(),
                        'department': department
                    }
                    if db.create_ticket(ticket_data):
                        st.success(f"✓ Ticket {new_id} created successfully!")
                    else:
                        st.error("❌ Failed to create ticket. ID may already exist.")
                else:
                    st.warning("⚠️ Please fill in required fields (ID, Title, Requester)")
    
    elif action == "Update Existing":
        tickets = db.get_all_tickets()
        ticket_ids = [tkt[0] for tkt in tickets]
        
        selected_id = st.selectbox("Select Ticket to Update", ticket_ids)
        
        if selected_id:
            ticket = db.get_ticket(selected_id)
            
            with st.form("update_ticket_form"):
                st.markdown(f"#### Update Ticket: {selected_id}")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    new_status = st.selectbox("Status", ["Open", "In Progress", "Waiting for User", "Resolved"],
                                             index=["Open", "In Progress", "Waiting for User", "Resolved"].index(ticket[5]) if ticket[5] in ["Open", "In Progress", "Waiting for User", "Resolved"] else 0)
                    new_priority = st.selectbox("Priority", ["Critical", "High", "Medium", "Low"],
                                               index=["Critical", "High", "Medium", "Low"].index(ticket[4]) if ticket[4] in ["Critical", "High", "Medium", "Low"] else 0)
                
                with col2:
                    new_assigned = st.selectbox("Assigned To", ["tech_support_01", "tech_support_02", "tech_support_03"])
                    resolution_time = st.number_input("Resolution Time (hours)", value=float(ticket[11]) if ticket[11] else 0.0, min_value=0.0)
                    sla_met = st.selectbox("SLA Met", ["Yes", "No", "Pending"])
                    satisfaction = st.slider("Satisfaction Rating", 1, 5, int(ticket[14]) if ticket[14] else 3)
                
                if st.form_submit_button("Update Ticket", use_container_width=True):
                    updates = {
                        'status': new_status,
                        'priority': new_priority,
                        'assigned_to': new_assigned
                    }
                    if new_status == "Resolved":
                        updates['resolved_at'] = datetime.now().isoformat()
                        updates['resolution_time_hours'] = resolution_time
                        updates['sla_met'] = sla_met
                        updates['satisfaction_rating'] = satisfaction
                    
                    if db.update_ticket(selected_id, **updates):
                        st.success(f"✓ Ticket {selected_id} updated!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to update ticket.")
    
    elif action == "Delete":
        tickets = db.get_all_tickets()
        ticket_ids = [tkt[0] for tkt in tickets]
        
        selected_id = st.selectbox("Select Ticket to Delete", ticket_ids)
        
        if selected_id:
            st.warning(f"⚠️ Are you sure you want to delete ticket {selected_id}?")
            
            if st.button("🗑️ Delete Ticket", type="primary"):
                if db.delete_ticket(selected_id):
                    st.success(f"✓ Ticket {selected_id} deleted!")
                    st.rerun()
                else:
                    st.error("❌ Failed to delete ticket.")


def render_ai_tab(stats: dict):
    """Render AI Assistant tab for IT Operations domain."""
    st.markdown("### 🤖 AI IT Operations Advisor")
    st.markdown("*Domain-restricted AI assistant for IT operations analysis only*")
    
    try:
        from ai_assistant import get_domain_assistant
        assistant = get_domain_assistant('it_operations')
        db = st.session_state.db
        
        if assistant is None or not assistant.is_configured():
            st.warning("""
            ⚠️ **IT Operations AI Assistant Not Configured**
            
            To enable this AI assistant, please:
            1. Get a Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey)
            2. Create a `.env` file in the project root
            3. Add: `GEMINI_API_KEY_IT=your_api_key_here`
            4. Restart the application
            
            **Note:** Each domain requires its own separate API key for security isolation.
            """)
            return
        
        # Domain restriction notice
        st.info("🔒 This AI assistant can ONLY answer questions about IT operations topics. It has access to IT ticket data only.")
        
        # Quick analysis button
        if st.button("🔍 Analyze IT Performance", use_container_width=True):
            with st.spinner("Analyzing tickets..."):
                analysis = assistant.analyze_domain_data(db)
                st.markdown("#### Analysis Results")
                st.markdown(analysis)
        
        st.markdown("---")
        
        # Chat interface
        st.markdown("#### Ask the IT Operations AI")
        
        if 'it_chat' not in st.session_state:
            st.session_state.it_chat = []
        
        # Display chat history
        chat_container = st.container()
        with chat_container:
            for msg in st.session_state.it_chat:
                if msg["role"] == "user":
                    st.markdown(f"**🧑 You:** {msg['content']}")
                else:
                    st.markdown(f"**🤖 AI:** {msg['content']}")
                st.markdown("---")
        
        # Chat input using text_input (works inside tabs)
        col1, col2 = st.columns([5, 1])
        with col1:
            prompt = st.text_input("Ask about IT operations, ticket management, or performance optimization...", 
                                   key="it_input", label_visibility="collapsed",
                                   placeholder="Ask about IT operations, ticket management, or performance optimization...")
        with col2:
            send_btn = st.button("Send", key="it_send", use_container_width=True)
        
        if send_btn and prompt:
            st.session_state.it_chat.append({"role": "user", "content": prompt})
            
            with st.spinner("Thinking..."):
                response = assistant.chat(prompt, db)
            
            st.session_state.it_chat.append({"role": "assistant", "content": response})
            st.rerun()
    
    except ImportError:
        st.error("AI Assistant module not found.")

