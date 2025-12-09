"""
Data Science Domain Dashboard
Addresses: Data Governance & Discovery - Resource consumption and data source dependency analysis
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta


def render_datascience_page():
    """Render the Data Science dashboard."""
    st.markdown("# 📊 Data Science Dashboard")
    st.markdown("*Data Governance & Discovery Platform*")
    
    # Get database instance
    db = st.session_state.db
    
    # Load dataset metadata
    df = db.get_datasets_dataframe()
    
    if df.empty:
        st.warning("No dataset metadata available. Please load sample data.")
        if st.button("Load Sample Data"):
            db.load_all_sample_data()
            st.rerun()
        return
    
    # Convert datetime columns
    df['upload_date'] = pd.to_datetime(df['upload_date'])
    df['last_accessed'] = pd.to_datetime(df['last_accessed'])
    
    # Get statistics
    stats = db.get_dataset_stats()
    
    # ============== KEY METRICS ==============
    st.markdown("### 📈 Key Metrics")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(
            "Total Datasets",
            stats['total'],
            help="Total datasets in catalog"
        )
    
    with col2:
        st.metric(
            "Total Storage",
            f"{stats['total_size_gb']} GB",
            help="Total storage consumption"
        )
    
    with col3:
        active_count = stats['by_status'].get('Active', 0)
        st.metric(
            "Active Datasets",
            active_count,
            delta=f"{round(active_count/stats['total']*100, 1)}% of total" if stats['total'] > 0 else "0%"
        )
    
    with col4:
        deprecated_count = stats['by_status'].get('Deprecated', 0)
        st.metric(
            "Deprecated",
            deprecated_count,
            delta="Needs archiving review" if deprecated_count > 0 else "Clean",
            delta_color="inverse" if deprecated_count > 0 else "normal"
        )
    
    with col5:
        st.metric(
            "Avg Quality Score",
            f"{stats['avg_quality_score']}%",
            help="Average data quality score"
        )
    
    st.markdown("---")
    
    # ============== TABS ==============
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
    
    # ============== RESOURCE CONSUMPTION ANALYSIS (Key Insight) ==============
    st.markdown("### 🎯 Resource Consumption Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Storage by department
        dept_data = []
        for dept, data in stats['by_department'].items():
            dept_data.append({
                'Department': dept,
                'Size (GB)': round(data['size_mb'] / 1024, 2),
                'Dataset Count': data['count']
            })
        dept_df = pd.DataFrame(dept_data).sort_values('Size (GB)', ascending=False)
        
        fig = px.bar(
            dept_df,
            x='Department',
            y='Size (GB)',
            title='Storage Consumption by Department',
            color='Size (GB)',
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
        # Dataset count by department
        fig = px.pie(
            dept_df,
            values='Dataset Count',
            names='Department',
            title='Dataset Distribution by Department',
            color_discrete_sequence=px.colors.sequential.Plasma_r,
            hole=0.4
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white')
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Key insight callout - Top consumer
    if dept_data:
        top_dept = dept_df.iloc[0]
        st.markdown(f"""
        <div style="padding: 20px; background: linear-gradient(145deg, rgba(0, 212, 255, 0.2), rgba(0, 212, 255, 0.1)); 
                    border-radius: 16px; border-left: 4px solid #00d4ff; margin: 20px 0;">
            <h4 style="color: #00d4ff; margin: 0 0 10px 0;">📊 Top Resource Consumer: {top_dept['Department']}</h4>
            <p style="color: white; margin: 0;">
                The <strong>{top_dept['Department']}</strong> department consumes <strong>{top_dept['Size (GB)']} GB</strong> 
                across <strong>{top_dept['Dataset Count']}</strong> datasets. 
                Consider reviewing large datasets for archiving opportunities.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ============== SIZE DISTRIBUTION ==============
    st.markdown("### 📦 Dataset Size Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Size distribution histogram
        fig = px.histogram(
            df,
            x='size_mb',
            nbins=20,
            title='Dataset Size Distribution (MB)',
            color_discrete_sequence=['#00d4ff']
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            xaxis_title="Size (MB)",
            yaxis_title="Count"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Size categories
        def categorize_size(size):
            if size < 100:
                return 'Small (<100 MB)'
            elif size < 500:
                return 'Medium (100-500 MB)'
            elif size < 1000:
                return 'Large (500-1000 MB)'
            else:
                return 'Very Large (>1 GB)'
        
        df['size_category'] = df['size_mb'].apply(categorize_size)
        size_cats = df['size_category'].value_counts()
        
        fig = px.pie(
            values=size_cats.values,
            names=size_cats.index,
            title='Datasets by Size Category',
            color_discrete_sequence=['#06d6a0', '#ffd166', '#f77f00', '#f72585']
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white')
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # ============== DATA QUALITY ANALYSIS ==============
    st.markdown("### ✅ Data Quality Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Quality score by department
        quality_by_dept = df.groupby('source_department')['quality_score'].mean().sort_values(ascending=True)
        
        colors = ['#f72585' if q < 80 else '#ffd166' if q < 90 else '#06d6a0' for q in quality_by_dept.values]
        
        fig = px.bar(
            x=quality_by_dept.values,
            y=quality_by_dept.index,
            orientation='h',
            title='Average Quality Score by Department',
            color=quality_by_dept.values,
            color_continuous_scale='RdYlGn'
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            showlegend=False,
            xaxis_title="Quality Score (%)",
            yaxis_title=""
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Quality vs Size scatter
        fig = px.scatter(
            df,
            x='size_mb',
            y='quality_score',
            color='source_department',
            size='row_count',
            title='Quality Score vs Size (bubble = row count)',
            hover_data=['name']
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            xaxis_title="Size (MB)",
            yaxis_title="Quality Score (%)"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # ============== DATA SOURCE DEPENDENCY ==============
    st.markdown("### 🔗 Data Source Dependency Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # File format distribution
        format_counts = df['file_format'].value_counts()
        
        fig = px.bar(
            x=format_counts.index,
            y=format_counts.values,
            title='Dataset File Formats',
            color=format_counts.values,
            color_continuous_scale='Viridis'
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            showlegend=False,
            xaxis_title="Format",
            yaxis_title="Count"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Data freshness (days since last access)
        df['days_since_access'] = (datetime.now() - df['last_accessed']).dt.days
        
        fig = px.histogram(
            df,
            x='days_since_access',
            nbins=15,
            title='Days Since Last Access',
            color_discrete_sequence=['#9d4edd']
        )
        fig.add_vline(x=30, line_dash="dash", line_color="#ffd166", annotation_text="30 days")
        fig.add_vline(x=90, line_dash="dash", line_color="#f72585", annotation_text="90 days")
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            xaxis_title="Days",
            yaxis_title="Count"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # ============== ARCHIVING RECOMMENDATIONS ==============
    st.markdown("### 📁 Archiving Recommendations")
    
    # Identify candidates for archiving
    archive_candidates = df[
        (df['status'] == 'Deprecated') | 
        (df['days_since_access'] > 90) |
        (df['quality_score'] < 70)
    ].copy()
    
    if not archive_candidates.empty:
        archive_candidates['reason'] = archive_candidates.apply(
            lambda x: 'Deprecated' if x['status'] == 'Deprecated' 
                     else 'Stale (>90 days)' if x['days_since_access'] > 90
                     else 'Low Quality (<70%)',
            axis=1
        )
        
        st.markdown(f"**{len(archive_candidates)} datasets recommended for archiving review:**")
        
        st.dataframe(
            archive_candidates[['dataset_id', 'name', 'source_department', 'size_mb', 'quality_score', 'days_since_access', 'reason']].sort_values('size_mb', ascending=False),
            use_container_width=True
        )
        
        potential_savings = archive_candidates['size_mb'].sum() / 1024
        st.markdown(f"""
        <div style="padding: 15px; background: rgba(6, 214, 160, 0.2); border-radius: 12px; border-left: 4px solid #06d6a0; color: #ffffff;">
            <strong style="color: #06d6a0;">💰 Potential Storage Savings:</strong> {round(potential_savings, 2)} GB by archiving recommended datasets
        </div>
        """, unsafe_allow_html=True)
    else:
        st.success("✓ No datasets currently require archiving review.")


def render_explorer_tab(df: pd.DataFrame):
    """Render dataset explorer with filtering."""
    st.markdown("### 🔍 Dataset Explorer")
    
    # Filters
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        dept_filter = st.multiselect(
            "Department",
            options=df['source_department'].unique().tolist(),
            default=df['source_department'].unique().tolist()
        )
    
    with col2:
        status_filter = st.multiselect(
            "Status",
            options=df['status'].unique().tolist(),
            default=df['status'].unique().tolist()
        )
    
    with col3:
        format_filter = st.multiselect(
            "Format",
            options=df['file_format'].unique().tolist(),
            default=df['file_format'].unique().tolist()
        )
    
    with col4:
        search_term = st.text_input("Search", placeholder="Search datasets...")
    
    # Size filter
    col1, col2 = st.columns(2)
    with col1:
        min_size = st.number_input("Min Size (MB)", value=0.0, min_value=0.0)
    with col2:
        max_size = st.number_input("Max Size (MB)", value=float(df['size_mb'].max()), min_value=0.0)
    
    # Apply filters
    filtered_df = df[
        (df['source_department'].isin(dept_filter)) &
        (df['status'].isin(status_filter)) &
        (df['file_format'].isin(format_filter)) &
        (df['size_mb'] >= min_size) &
        (df['size_mb'] <= max_size)
    ]
    
    if search_term:
        filtered_df = filtered_df[
            filtered_df['name'].str.contains(search_term, case=False, na=False) |
            filtered_df['description'].str.contains(search_term, case=False, na=False)
        ]
    
    st.markdown(f"*Showing {len(filtered_df)} of {len(df)} datasets*")
    
    # Display table
    display_cols = ['dataset_id', 'name', 'source_department', 'file_format', 'size_mb', 'row_count', 'quality_score', 'status', 'upload_date']
    st.dataframe(
        filtered_df[display_cols].sort_values('upload_date', ascending=False),
        use_container_width=True,
        height=400
    )
    
    # Dataset details
    st.markdown("### 📋 Dataset Details")
    selected_dataset = st.selectbox(
        "Select dataset to view details",
        options=filtered_df['dataset_id'].tolist(),
        format_func=lambda x: f"{x}: {filtered_df[filtered_df['dataset_id']==x]['name'].values[0]}"
    )
    
    if selected_dataset:
        dataset = filtered_df[filtered_df['dataset_id'] == selected_dataset].iloc[0]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            **ID:** {dataset['dataset_id']}  
            **Name:** {dataset['name']}  
            **Department:** {dataset['source_department']}  
            **Format:** {dataset['file_format']}  
            **Status:** {dataset['status']}  
            """)
        
        with col2:
            st.markdown(f"""
            **Size:** {dataset['size_mb']} MB  
            **Rows:** {dataset['row_count']:,}  
            **Columns:** {dataset['column_count']}  
            **Quality Score:** {dataset['quality_score']}%  
            """)
        
        with col3:
            st.markdown(f"""
            **Uploaded By:** {dataset['uploaded_by']}  
            **Upload Date:** {dataset['upload_date']}  
            **Last Accessed:** {dataset['last_accessed']}  
            **Location:** {dataset['storage_location']}  
            """)
        
        st.markdown(f"**Description:** {dataset['description']}")


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
            storage_location = st.text_input("Storage Location", placeholder="/data/dept/filename.csv")
            uploaded_by = st.text_input("Uploaded By", placeholder="username")
            
            if st.form_submit_button("Register Dataset", use_container_width=True):
                if new_id and name and uploaded_by:
                    dataset_data = {
                        'dataset_id': new_id,
                        'name': name,
                        'description': description,
                        'source_department': source_dept,
                        'file_format': file_format,
                        'size_mb': size_mb,
                        'row_count': row_count,
                        'column_count': column_count,
                        'uploaded_by': uploaded_by,
                        'upload_date': datetime.now().isoformat(),
                        'last_accessed': datetime.now().isoformat(),
                        'quality_score': quality_score,
                        'status': 'Active',
                        'storage_location': storage_location
                    }
                    if db.create_dataset(dataset_data):
                        st.success(f"✓ Dataset {new_id} registered successfully!")
                    else:
                        st.error("❌ Failed to register dataset. ID may already exist.")
                else:
                    st.warning("⚠️ Please fill in required fields (ID, Name, Uploaded By)")
    
    elif action == "Update Existing":
        datasets = db.get_all_datasets()
        dataset_ids = [ds[0] for ds in datasets]
        
        selected_id = st.selectbox("Select Dataset to Update", dataset_ids)
        
        if selected_id:
            dataset = db.get_dataset(selected_id)
            
            with st.form("update_dataset_form"):
                st.markdown(f"#### Update Dataset: {selected_id}")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    new_status = st.selectbox("Status", ["Active", "Archived", "Deprecated"],
                                             index=["Active", "Archived", "Deprecated"].index(dataset[12]) if dataset[12] in ["Active", "Archived", "Deprecated"] else 0)
                    new_quality = st.slider("Quality Score", 0.0, 100.0, float(dataset[11]) if dataset[11] else 80.0)
                
                with col2:
                    new_size = st.number_input("Size (MB)", value=float(dataset[5]) if dataset[5] else 0.0, min_value=0.0)
                    new_rows = st.number_input("Row Count", value=int(dataset[6]) if dataset[6] else 0, min_value=0)
                
                if st.form_submit_button("Update Dataset", use_container_width=True):
                    updates = {
                        'status': new_status,
                        'quality_score': new_quality,
                        'size_mb': new_size,
                        'row_count': new_rows,
                        'last_accessed': datetime.now().isoformat()
                    }
                    
                    if db.update_dataset(selected_id, **updates):
                        st.success(f"✓ Dataset {selected_id} updated!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to update dataset.")
    
    elif action == "Delete":
        datasets = db.get_all_datasets()
        dataset_ids = [ds[0] for ds in datasets]
        
        selected_id = st.selectbox("Select Dataset to Delete", dataset_ids)
        
        if selected_id:
            st.warning(f"⚠️ Are you sure you want to delete dataset {selected_id}?")
            
            if st.button("🗑️ Delete Dataset", type="primary"):
                if db.delete_dataset(selected_id):
                    st.success(f"✓ Dataset {selected_id} deleted!")
                    st.rerun()
                else:
                    st.error("❌ Failed to delete dataset.")


def render_ai_tab(stats: dict):
    """Render AI Assistant tab for Data Science domain."""
    st.markdown("### 🤖 AI Data Governance Advisor")
    st.markdown("*Domain-restricted AI assistant for data science analysis only*")
    
    try:
        from ai_assistant import get_domain_assistant
        assistant = get_domain_assistant('datascience')
        db = st.session_state.db
        
        if assistant is None or not assistant.is_configured():
            st.warning("""
            ⚠️ **Data Science AI Assistant Not Configured**
            
            To enable this AI assistant, please:
            1. Get a Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey)
            2. Create a `.env` file in the project root
            3. Add: `GEMINI_API_KEY_DATA=your_api_key_here`
            4. Restart the application
            
            **Note:** Each domain requires its own separate API key for security isolation.
            """)
            return
        
        # Domain restriction notice
        st.info("🔒 This AI assistant can ONLY answer questions about data science topics. It has access to dataset catalog data only.")
        
        # Quick analysis button
        if st.button("🔍 Analyze Data Governance", use_container_width=True):
            with st.spinner("Analyzing datasets..."):
                analysis = assistant.analyze_domain_data(db)
                st.markdown("#### Analysis Results")
                st.markdown(analysis)
        
        st.markdown("---")
        
        # Chat interface
        st.markdown("#### Ask the Data Science AI")
        
        if 'ds_chat' not in st.session_state:
            st.session_state.ds_chat = []
        
        # Display chat history
        chat_container = st.container()
        with chat_container:
            for msg in st.session_state.ds_chat:
                if msg["role"] == "user":
                    st.markdown(f"**🧑 You:** {msg['content']}")
                else:
                    st.markdown(f"**🤖 AI:** {msg['content']}")
                st.markdown("---")
        
        # Chat input using text_input (works inside tabs)
        col1, col2 = st.columns([5, 1])
        with col1:
            prompt = st.text_input("Ask about data governance, quality, or archiving policies...", 
                                   key="ds_input", label_visibility="collapsed",
                                   placeholder="Ask about data governance, quality, or archiving policies...")
        with col2:
            send_btn = st.button("Send", key="ds_send", use_container_width=True)
        
        if send_btn and prompt:
            st.session_state.ds_chat.append({"role": "user", "content": prompt})
            
            with st.spinner("Thinking..."):
                response = assistant.chat(prompt, db)
            
            st.session_state.ds_chat.append({"role": "assistant", "content": response})
            st.rerun()
    
    except ImportError:
        st.error("AI Assistant module not found.")

