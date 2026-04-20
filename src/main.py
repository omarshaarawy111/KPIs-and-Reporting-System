# app.py
# Libraries
import streamlit as st
import numpy as np
import pandas as pd
import warnings
import math
import plotly.express as px
import plotly.graph_objects as go
warnings.filterwarnings('ignore')

# Import modules
from auth import authenticate_user
from ui import small_header, centered_metric, sidebar_style
from data_processing import format_display_name, load_and_combine_files
from reports import create_download_link, generate_html_report

if __name__ == "__main__":
    # Layout
    st.set_page_config(
        layout="wide",
        page_icon='📊',
        page_title='Metrics Monitor'
    )

    # Login
    is_logged_in = st.session_state.get('is_logged_in', False)
    if not is_logged_in:
        st.markdown(
            '''
            <div style="text-align: center;">
                <img src="#" alt="Logo" style="width: 600px; height: auto;">
            </div>
            ''',
            unsafe_allow_html=True
        )

        st.markdown('<h1 style="text-align: center;  font-size:28px;">Metrics Monitor</h1>', unsafe_allow_html=True)

        email = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login_button = st.button("Login")

        if login_button:
            if authenticate_user(email, password):
                st.session_state.is_logged_in = True
                st.success("Logged in successfully!")
                st.rerun()
            else:
                st.error("Wrong Email or Password.")

    else:
        # Upload
        st.empty()
        st.markdown("<h2 style='text-align: left;'>Start Analysing...</h2>", unsafe_allow_html=True)

        uploaded_files = st.file_uploader("Choose files", type=["csv"], accept_multiple_files=True, key="file_uploader")

        if uploaded_files:

            # Load and combine all files
            df = load_and_combine_files(uploaded_files)

            if not df.empty:
                st.success(f"Successfully loaded {len(uploaded_files)} file(s) with {len(df)} total records!")

                # Preprocessing
                df = df.rename(columns={"Justfication": "Justification"})
                df = df.rename(columns={"Desciption": "Description"})
                df['Finished within SLA'] = df['Finished within SLA'].fillna('None').astype(str).str.strip()
                df['Complexity'] = df['Complexity'].fillna(0)
                df['Uncertainty'] = df['Uncertainty'].fillna(0)
                df['Time'] = df['Time'].fillna(0)
                df['Average'] = df['Average'].fillna(0)
                df['Description'] = df['Description'].fillna('None').astype(str).str.strip()
                df['Dev Agency Contribution'] = df['Dev Agency Contribution'].fillna('None').astype(str).str.strip()
                df['Justification'] = df['Justification'].fillna('None').astype(str).str.strip()
                months = ["January", "February", "March", "April", "May", "June",
                        "July", "August", "September", "October", "November", "December"]

                # Sidebar Filters
                sidebar_style()
                st.sidebar.title('Filters')
                show_data = st.sidebar.checkbox('Show All Data', key=1)
                show_done = st.sidebar.checkbox('Show Done Tasks', key=2)
                show_pending = st.sidebar.checkbox('Show Pending Tasks', key=3)
                show_justification = st.sidebar.checkbox('Show Justifications', key=4)

                # Determine if single assignee or multiple
                all_assignees = df['Assignee Name'].dropna().unique().tolist()
                is_single_assignee = len(all_assignees) == 1

                st.sidebar.title('Assignee')
                if is_single_assignee:
                    # For single assignee, show the name as default and disable selection
                    assignee = st.sidebar.multiselect(
                        '',
                        all_assignees,
                        default=all_assignees,
                        disabled=True,
                        key=5
                    )
                else:
                    # For multiple assignees, allow selection without "All" when specific assignees are selected
                    assignee_options = all_assignees

                    # Initialize session state for assignee selection
                    if 'selected_assignees' not in st.session_state:
                        st.session_state.selected_assignees = all_assignees

                    # Handle selection changes
                    def update_assignee_selection():
                        current_selection = st.session_state.assignee_selector
                        st.session_state.selected_assignees = current_selection

                    # Display the multiselect with the updated handler
                    assignee = st.sidebar.multiselect(
                        '',
                        assignee_options,
                        default=st.session_state.selected_assignees,
                        key='assignee_selector',
                        on_change=update_assignee_selection
                    )

                st.sidebar.title('Year')
                year = st.sidebar.multiselect('', df['Year'].dropna().unique(), key=6)
                st.sidebar.title('Month')
                month = st.sidebar.multiselect('', months, key=7)

                week_options = ['Week 1', 'Week 2', 'Week 3', 'Week 4']
                if month:
                    st.sidebar.title('Week')
                    week = st.sidebar.multiselect('', week_options, key=8)
                else:
                    week = []

                # Apply filters
                filtered_df = df.copy()

                if 'Assignee Name' in df.columns:
                    df['Assignee Name'] = df['Assignee Name'].apply(format_display_name)

                if assignee:
                    filtered_df = filtered_df[filtered_df['Assignee Name'].isin(assignee)]

                if year:
                    filtered_df = filtered_df[filtered_df['Year'].isin(year)]

                if month:
                    filtered_df = filtered_df[filtered_df['Month'].isin(month)]
                    if filtered_df.empty:
                        filtered_df = pd.DataFrame(columns=df.columns)

                if month and week:
                    conditions = []
                    for m in month:
                        for w in week:
                            if w == 'Week 1':
                                day_min, day_max = 1, 7
                            elif w == 'Week 2':
                                day_min, day_max = 8, 14
                            elif w == 'Week 3':
                                day_min, day_max = 15, 21
                            elif w == 'Week 4':
                                day_min, day_max = 22, 31
                            conditions.append((filtered_df['Month'] == m) & (filtered_df['Day'] >= day_min) & (filtered_df['Day'] <= day_max))
                    if conditions:
                        combined_condition = conditions[0]
                        for cond in conditions[1:]:
                            combined_condition |= cond
                        filtered_df = filtered_df[combined_condition]

                # Determine columns to display based on filters
                display_cols_all = df.columns.tolist()
                display_cols_just = df.columns.tolist()

                if len(year) == 1:
                    display_cols_all = [col for col in display_cols_all if col != 'Year']
                    display_cols_just = [col for col in display_cols_just if col != 'Year']

                if len(month) == 1:
                    display_cols_all = [col for col in display_cols_all if col != 'Month']
                    display_cols_just = [col for col in display_cols_just if col != 'Month']

                # For all data
                if show_data:
                    st.header('All Data...')
                    display_df = filtered_df[display_cols_all].copy()

                    # Sort by Year, Month if available
                    if 'Year' in display_df.columns and 'Month' in display_df.columns:
                        months_order = ["January", "February", "March", "April", "May", "June",
                                      "July", "August", "September", "October", "November", "December"]
                        display_df['Month'] = pd.Categorical(display_df['Month'], categories=months_order, ordered=True)
                        display_df = display_df.sort_values(['Year', 'Month'])
                        display_df['Year'] = display_df['Year'].astype(int)

                    display_df.reset_index(drop=True, inplace=True)
                    display_df.index = display_df.index + 1
                    if 'Assignee Name' in display_df.columns:
                        display_df['Assignee Name'] = display_df['Assignee Name'].apply(format_display_name)
                    st.dataframe(display_df, use_container_width=True)

                # For done tasks
                if show_done:
                    st.header('Done Tasks...')
                    done_df = filtered_df[filtered_df['Status'].str.lower() == 'done']
                    display_done_df = done_df[display_cols_all].copy()

                    # Sort by Year, Month if available
                    if 'Year' in display_done_df.columns and 'Month' in display_done_df.columns:
                        months_order = ["January", "February", "March", "April", "May", "June",
                                      "July", "August", "September", "October", "November", "December"]
                        display_done_df['Month'] = pd.Categorical(display_done_df['Month'], categories=months_order, ordered=True)
                        display_done_df = display_done_df.sort_values(['Year', 'Month'])
                        display_done_df['Year'] = display_done_df['Year'].astype(int)

                    display_done_df.reset_index(drop=True, inplace=True)
                    display_done_df.index = display_done_df.index + 1
                    if 'Assignee Name' in display_done_df.columns:
                        display_done_df['Assignee Name'] = display_done_df['Assignee Name'].apply(format_display_name)
                    st.dataframe(display_done_df, use_container_width=True)

                # For pending tasks
                if show_pending:
                    st.header('Pending Tasks...')
                    pend_df = filtered_df[
                        (filtered_df['Status'].str.lower() == 'in progress')
                    ]
                    display_pend_df = pend_df[display_cols_all].copy()

                    # Sort by Year, Month if available
                    if not display_pend_df.empty:
                        if 'Year' in display_pend_df.columns and 'Month' in display_pend_df.columns:
                            months_order = ["January", "February", "March", "April", "May", "June",
                                          "July", "August", "September", "October", "November", "December"]
                            display_pend_df['Month'] = pd.Categorical(display_pend_df['Month'], categories=months_order, ordered=True)
                            display_pend_df = display_pend_df.sort_values(['Year', 'Month'])
                            display_pend_df['Year'] = display_pend_df['Year'].astype(int)

                    display_pend_df.reset_index(drop=True, inplace=True)
                    display_pend_df.index = display_pend_df.index + 1
                    if 'Assignee Name' in display_pend_df.columns:
                        display_pend_df['Assignee Name'] = display_pend_df['Assignee Name'].apply(format_display_name)
                    st.dataframe(display_pend_df, use_container_width=True)

                # For justifications
                if show_justification:
                    st.header('All Justifications...')
                    just_df = filtered_df[filtered_df['Justification'] != 'None']
                    if not just_df.empty:
                        just_cols = display_cols_just.copy()
                        justification_col = 'Justification'
                        just_cols.insert(2, just_cols.pop(just_cols.index(justification_col)))
                        display_just_df = just_df[just_cols].copy()

                        # Sort by Year, Month if available
                        if 'Year' in display_just_df.columns and 'Month' in display_just_df.columns:
                            months_order = ["January", "February", "March", "April", "May", "June",
                                          "July", "August", "September", "October", "November", "December"]
                            display_just_df['Month'] = pd.Categorical(display_just_df['Month'], categories=months_order, ordered=True)
                            display_just_df = display_just_df.sort_values(['Year', 'Month'])
                            display_just_df['Year'] = display_just_df['Year'].astype(int)

                        display_just_df.reset_index(drop=True, inplace=True)
                        display_just_df.index = display_just_df.index + 1
                        if 'Assignee Name' in display_just_df.columns:
                            display_just_df['Assignee Name'] = display_just_df['Assignee Name'].apply(format_display_name)
                        st.dataframe(display_just_df, use_container_width=True)
                    else:
                        st.write("No justifications found.")

                # Header
                st.markdown("<h2 style='text-align: center;'>Welcome to Metrics Monitor Insights</h2>", unsafe_allow_html=True)

                # Export button with HTML download
                df_non_internal = filtered_df[~filtered_df['Brand'].str.lower().str.startswith('internal_')]
                col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
                with col3:
                    if st.button('Generate Report 📄', use_container_width=True):
                        try:
                            html_content, report_name = generate_html_report(
                                filtered_df, df_non_internal, assignee, month, year,
                                show_data, show_done, show_pending, show_justification, week
                            )

                            st.download_button(
                                label="Download Report ⬇️",
                                data=html_content,
                                file_name=f"{report_name}.html",
                                mime="text/html",
                                use_container_width=True
                            )

                            st.success("Report generated successfully!\n\nYou can download it now.")
                        except Exception as e:
                            st.error(f"Error generating report: {str(e)}")

                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)

                # Metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    small_header('📋 Total Tasks')
                    total_tasks = filtered_df['Task Name'].shape[0] if not filtered_df.empty else 0
                    centered_metric(" ", total_tasks)
                with col2:
                    small_header('⚖️ Total Weights')
                    total_weights = int(filtered_df['Average'].sum()) if not filtered_df.empty else 0
                    centered_metric(" ", total_weights)
                with col3:
                    small_header('⏱️ SLA Completion')
                    if not filtered_df.empty:
                        filtered_df_sla = filtered_df[
                            (filtered_df['Status'].str.lower() == 'done') &
                            (filtered_df['Finished within SLA'].str.lower().isin(['yes', 'no']))
                        ]
                        sla_ratio = (filtered_df_sla['Finished within SLA'].str.lower() == 'yes').mean() * 100 if not filtered_df_sla.empty else 0
                        sla_ratio_ceil = math.ceil(sla_ratio) if not np.isnan(sla_ratio) else 0
                    else:
                        sla_ratio_ceil = 0
                    centered_metric(" ", f"{sla_ratio_ceil} %")

                st.markdown("<hr>", unsafe_allow_html=True)

                col1, col2, col3 = st.columns(3)
                with col1:
                    small_header('📏 Task Average Size')
                    if not filtered_df.empty:
                        total_tasks = filtered_df['Task Name'].shape[0]
                        total_weights = int(filtered_df['Average'].sum())
                        task_average_size = np.round((total_weights / total_tasks),1)
                    else:
                        task_average_size = 0
                    centered_metric(" ", task_average_size)
                with col2:
                    small_header('🌍 External Missions')
                    if not filtered_df.empty:
                        external_tasks = filtered_df[filtered_df['Brand'].str.lower().str.startswith('external_')]
                        total_tasks_external = external_tasks['Brand'].nunique()
                    else:
                        total_tasks_external = 0
                    centered_metric(" ", total_tasks_external)
                with col3:
                    small_header('🏷️ Total Brands')
                    if not filtered_df.empty:
                        df_non_internal = filtered_df[~filtered_df['Brand'].str.lower().str.startswith('internal_')]
                        total_brands = df_non_internal['Brand'].nunique() if not df_non_internal.empty else 0
                    else:
                        total_brands = 0
                    centered_metric(" ", total_brands)

                st.markdown("<hr>", unsafe_allow_html=True)

                col1, col2, col3 = st.columns(3)
                with col1:
                    small_header('✅ Done Tasks')
                    total_done = filtered_df[filtered_df['Status'].str.lower() == 'done'].shape[0] if not filtered_df.empty else 0
                    centered_metric(" ", total_done)
                with col2:
                    small_header('⌛ Pending Tasks')
                    if not filtered_df.empty:
                        total_pending = filtered_df[
                            (filtered_df['Status'].str.lower() == 'in progress')].shape[0]
                    else:
                        total_pending = 0
                    centered_metric(" ", total_pending)
                with col3:
                    small_header('📝 Justifications')
                    total_justifications = filtered_df[filtered_df['Justification'].str.lower() != 'none'].shape[0] if not filtered_df.empty else 0
                    centered_metric(" ", total_justifications)

                st.markdown("<hr>", unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)

                # Assignee comparison tables - only if multiple assignees in filtered data
                if len(assignee) > 1:
                    # Calculate metrics per assignee
                    assignee_stats = []
                    for a in assignee:
                        assignee_df = filtered_df[filtered_df['Assignee Name'] == a]
                        if not assignee_df.empty:
                            stats = {
                                'Assignee': format_display_name(a),
                                'Total Tasks': assignee_df.shape[0],
                                'Total Weights': int(assignee_df['Average'].sum()),
                                'Done Tasks': assignee_df[assignee_df['Status'].str.lower() == 'done'].shape[0],
                                'Pending Tasks': assignee_df[
                                    (assignee_df['Status'].str.lower() == 'in progress')
                                ].shape[0],
                                'SLA Completion': math.ceil(
                                    assignee_df[
                                        (assignee_df['Status'].str.lower() == 'done') &
                                        (assignee_df['Finished within SLA'].str.lower().isin(['yes', 'no']))
                                    ]['Finished within SLA'].str.lower().value_counts(normalize=True).get('yes', 0) * 100
                                ),
                                'Task Average Size': np.round(int(assignee_df['Average'].sum()) / assignee_df['Task Name'].shape[0],1),
                                'External Missions': assignee_df[assignee_df['Brand'].str.lower().str.startswith('external_')]['Brand'].nunique(),
                                'Total Brands': assignee_df[~assignee_df['Brand'].str.lower().str.startswith('internal_')]['Brand'].nunique(),
                                'Justifications': assignee_df[assignee_df['Justification'].str.lower() != 'none'].shape[0]
                            }
                            assignee_stats.append(stats)

                    if assignee_stats:
                        st.markdown("<h4 style='text-align: center;'>Assignee Comparison</h4>", unsafe_allow_html=True)
                        assignee_df_stats = pd.DataFrame(assignee_stats)

                        # Champion table (Total Weights)
                        champion_table = assignee_df_stats.sort_values('Total Weights', ascending=False).reset_index(drop=True).rename(columns={'index': 'Order'})
                        champion_table.index.name = 'Order'
                        champion_table = champion_table[['Assignee', 'Total Weights']]
                        champion_table.index = champion_table.index + 1
                        st.markdown("<h5 style='text-align: center;'>Champion Table (Total Weights)</h5>", unsafe_allow_html=True)
                        st.dataframe(
                            champion_table,
                            use_container_width=True
                        )

                        # Detailed metrics table
                        detailed_metrics = assignee_df_stats[['Assignee', 'Total Tasks', 'SLA Completion',
                                                           'Task Average Size', 'External Missions', 'Total Brands',
                                                           'Done Tasks', 'Pending Tasks', 'Justifications']]

                        st.markdown("<h5 style='text-align: center;'>Detailed Assignee Metrics</h5>", unsafe_allow_html=True)
                        st.dataframe(
                            detailed_metrics.set_index('Assignee'),
                            use_container_width=True
                        )

                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)

                # Visualizations
                if not filtered_df.empty:
                    df_non_internal = filtered_df[~filtered_df['Brand'].str.lower().str.startswith('internal_')]

                    if is_single_assignee or len(assignee) == 1:
                        # Single assignee visuals
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown("<h5 style='text-align: center;'>Task Distribution by Brands</h5>", unsafe_allow_html=True)
                            if not df_non_internal.empty:
                                fig = px.histogram(df_non_internal, x='Brand', color='Brand', text_auto=True, color_discrete_sequence=px.colors.qualitative.Pastel)
                                fig.update_layout(xaxis_title='Brands', xaxis={'categoryorder': 'total descending'}, title='')
                                st.plotly_chart(fig, use_container_width=True)
                            else:
                                fig = go.Figure()
                                fig.update_layout(xaxis_title='Brands', yaxis_title='Count',
                                                title='', xaxis={'categoryorder': 'total descending'})
                                fig.add_annotation(text="No brand data available", xref="paper", yref="paper",
                                                x=0.5, y=0.5, showarrow=False)
                                st.plotly_chart(fig, use_container_width=True)

                        with col2:
                            st.markdown("<h5 style='text-align: center;'>Weights per Brand</h5>", unsafe_allow_html=True)
                            if not df_non_internal.empty:
                                fig = px.histogram(df_non_internal, x='Brand', y='Average', title='', color='Brand', text_auto=True, color_discrete_sequence=px.colors.qualitative.Pastel)
                                fig.update_layout(xaxis_title='Brands', yaxis_title='Weights', xaxis={'categoryorder': 'total descending'}, title='')
                                st.plotly_chart(fig, use_container_width=True)
                            else:
                                fig = go.Figure()
                                fig.update_layout(xaxis_title='Brands', yaxis_title='Weights',
                                                title='', xaxis={'categoryorder': 'total descending'})
                                fig.add_annotation(text="No brand data available", xref="paper", yref="paper",
                                                x=0.5, y=0.5, showarrow=False)
                                st.plotly_chart(fig, use_container_width=True)

                        st.markdown("<br>", unsafe_allow_html=True)
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown("<h5 style='text-align: center;'>Task Distribution by Priority (%)</h5>", unsafe_allow_html=True)
                            if not filtered_df.empty:
                                priority_counts = filtered_df['Priority'].value_counts().reset_index()
                                priority_counts.columns = ['Priority', 'Count']

                                fig = px.pie(
                                    priority_counts,
                                    names='Priority',
                                    values='Count',
                                    color_discrete_sequence=['#D32F2F', '#FFCDD2'],
                                    hole=0.3
                                )

                                fig.update_traces(
                                    textinfo='label+percent+value',
                                    showlegend=True,
                                    hovertemplate='%{label} : %{value} tasks, (%{percent})',
                                    texttemplate='%{percent}'
                                )

                                st.plotly_chart(fig, use_container_width=True)

                            else:
                                fig = go.Figure()
                                fig.update_layout(title='')
                                fig.add_annotation(text="No priority data available", xref="paper", yref="paper",
                                                x=0.5, y=0.5, showarrow=False)
                                st.plotly_chart(fig, use_container_width=True)

                        with col2:
                            st.markdown("<h5 style='text-align: center;'>SLA Completion (%)</h5>", unsafe_allow_html=True)
                            filtered_df_sla = filtered_df[
                                (filtered_df['Status'].str.lower() == 'done') &
                                (filtered_df['Finished within SLA'].str.lower().isin(['yes', 'no']))
                            ]
                            if not filtered_df_sla.empty:
                                sla_counts = filtered_df_sla['Finished within SLA'].value_counts().reset_index()
                                sla_counts.columns = ['Finished within SLA', 'Count']

                                # Build pie chart
                                fig = px.pie(
                                    sla_counts,
                                    names='Finished within SLA',
                                    values='Count',
                                    color_discrete_sequence=['#4CAF50', '#F44336'],
                                    hole=0.3
                                )

                                # Customize labels and hover
                                fig.update_traces(
                                    textinfo='label+percent+value',
                                    texttemplate='%{percent}',
                                    showlegend=True
                                )
                                st.plotly_chart(fig, use_container_width=True)
                            else:
                                fig = go.Figure()
                                fig.update_layout(title='')
                                fig.add_annotation(text="No SLA data available", xref="paper", yref="paper",
                                                x=0.5, y=0.5, showarrow=False)
                                st.plotly_chart(fig, use_container_width=True)

                        st.markdown("<br>", unsafe_allow_html=True)

                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown("<h5 style='text-align: center;'>Dev Agency Work</h5>", unsafe_allow_html=True)
                            filtered_df_dev = filtered_df[filtered_df['Dev Agency Contribution'].str.lower().isin(['yes', 'no'])]
                            if not filtered_df_dev.empty:
                                fig = px.histogram(filtered_df_dev, x='Dev Agency Contribution', title='', color='Dev Agency Contribution',
                                                color_discrete_map={'No': 'green', 'Yes': 'red'}, text_auto=True)
                                fig.update_layout(xaxis_title='Dev Agency Contribution', xaxis={'categoryorder': 'total descending'},
                                                title='')
                                st.plotly_chart(fig, use_container_width=True)
                            else:
                                fig = go.Figure()
                                fig.update_layout(xaxis_title='Dev Agency Contribution',
                                                title='', xaxis={'categoryorder': 'total descending'})
                                fig.add_annotation(text="No Dev Agency data available", xref="paper", yref="paper",
                                                x=0.5, y=0.5, showarrow=False)
                                st.plotly_chart(fig, use_container_width=True)

                        with col2:
                            st.markdown("<h5 style='text-align: center;'>Task Completion (%)</h5>", unsafe_allow_html=True)
                            if not filtered_df.empty:

                                status_counts = filtered_df['Status'].value_counts().reset_index()
                                status_counts.columns = ['Status', 'Count']

                                fig = px.pie(
                                    status_counts,
                                    names='Status',
                                    values='Count',
                                    color_discrete_sequence=['#2E7D32', '#EF6C00'],
                                    hole=0.3
                                )

                                fig.update_traces(
                                    textinfo='label+percent+value',
                                    showlegend=True,
                                    hovertemplate='%{label} : %{value} tasks, (%{percent})',
                                    texttemplate='%{percent}'
                                )
                                st.plotly_chart(fig, use_container_width=True)
                            else:
                                fig = go.Figure()
                                fig.update_layout(title='')
                                fig.add_annotation(text="No status data available", xref="paper", yref="paper",
                                                x=0.5, y=0.5, showarrow=False)
                                st.plotly_chart(fig, use_container_width=True)

                        st.markdown("<br>", unsafe_allow_html=True)

                        # Timeline
                        filtered_df['Month'] = pd.Categorical(filtered_df['Month'], categories=months, ordered=True)
                        filtered_df['Month_Num'] = filtered_df['Month'].apply(lambda x: months.index(x) + 1 if x in months else None)
                        filtered_df['Date'] = pd.to_datetime(
                            filtered_df[['Year', 'Month_Num']].dropna().astype(int).rename(columns={'Year': 'year', 'Month_Num': 'month'}).assign(day=1))
                        timeline_df = filtered_df.dropna(subset=['Date'])
                        if not timeline_df.empty:
                            st.markdown("<h5 style='text-align: center;'>Task Count Over Months</h5>", unsafe_allow_html=True)
                            timeline_df = timeline_df.groupby('Date').size().reset_index(name='Task Count')
                            fig = px.line(timeline_df, x='Date', y='Task Count', markers=True)
                            fig.update_layout(xaxis_title='Month', yaxis_title='Number of Tasks', title='')
                            st.plotly_chart(fig, use_container_width=True)

                            st.markdown("<h5 style='text-align: center;'>Weight Sum Over Months</h5>", unsafe_allow_html=True)
                            timeline_weight_df = filtered_df.dropna(subset=['Date'])
                            timeline_weight_df = timeline_weight_df.groupby('Date')['Average'].sum().reset_index(name='Total Weight')
                            fig = px.line(timeline_weight_df, x='Date', y='Total Weight', markers=True)
                            fig.update_layout(xaxis_title='Date', yaxis_title='Total Weight', title='')
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.markdown("<h5 style='text-align: center;'>Task Count Over Months</h5>", unsafe_allow_html=True)
                            fig = go.Figure()
                            fig.update_layout(xaxis_title='Month', yaxis_title='Number of Tasks', title='')
                            fig.add_annotation(text="No timeline data available", xref="paper", yref="paper",
                                            x=0.5, y=0.5, showarrow=False)
                            st.plotly_chart(fig, use_container_width=True)

                            st.markdown("<h5 style='text-align: center;'>Weight Sum Over Months</h5>", unsafe_allow_html=True)
                            fig = go.Figure()
                            fig.update_layout(xaxis_title='Month', yaxis_title='Total Weight', title='')
                            fig.add_annotation(text="No timeline data available", xref="paper", yref="paper",
                                            x=0.5, y=0.5, showarrow=False)
                            st.plotly_chart(fig, use_container_width=True)
                    else:
                        # Multiple assignees visuals - comparison mode

                        # First row: Task Count and Total Weights by Assignee
                        col1, col2 = st.columns(2)

                        with col1:
                            st.markdown("<h5 style='text-align: center;'>Task Count by Assignee</h5>", unsafe_allow_html=True)
                            assignee_tasks = filtered_df['Assignee Name'].value_counts().reset_index()
                            assignee_tasks.columns = ['Assignee', 'Task Count']
                            assignee_tasks['Assignee'] = assignee_tasks['Assignee'].apply(format_display_name)
                            assignee_tasks = assignee_tasks.sort_values('Task Count', ascending=False)  # Sort descending

                            # Create the bar chart
                            fig = px.bar(assignee_tasks,
                                        x='Assignee',
                                        y='Task Count',
                                        color='Assignee',
                                        text_auto=True,
                                        color_discrete_sequence=px.colors.qualitative.Pastel,
                                        category_orders={"Assignee": assignee_tasks['Assignee'].tolist()})  # Enforce order

                            # Update layout for better spacing and presentation
                            fig.update_traces(width=0.4)
                            fig.update_layout(
                                xaxis_title='Assignee',
                                yaxis_title='Task Count',
                                showlegend=True,
                                xaxis={
                                    'title_standoff': 25,  # Increased spacing for x-axis title
                                    'automargin': True,     # Prevent title cutoff
                                    'categoryorder': 'total descending'  # Alternative sorting method
                                },
                                margin=dict(l=50, r=50, b=100, t=50),  # Increased bottom margin
                                uniformtext_minsize=8,  # Ensure text fits
                                uniformtext_mode='hide'  # Hide text if doesn't fit
                            )

                            st.plotly_chart(fig, use_container_width=True)

                        with col2:
                            st.markdown("<h5 style='text-align: center;'>Total Weights by Assignee</h5>", unsafe_allow_html=True)
                            # Get data and sort by Total Weights in descending order
                            assignee_weights = filtered_df.groupby('Assignee Name')['Average'].sum().reset_index()
                            assignee_weights.columns = ['Assignee', 'Total Weights']
                            assignee_weights['Assignee'] = assignee_weights['Assignee'].apply(format_display_name)
                            assignee_weights = assignee_weights.sort_values('Total Weights', ascending=False)  # Sort descending

                            # Create the bar chart
                            fig = px.bar(assignee_weights,
                                        x='Assignee',
                                        y='Total Weights',
                                        color='Assignee',
                                        text_auto=True,
                                        color_discrete_sequence=px.colors.qualitative.Pastel,
                                        category_orders={"Assignee": assignee_weights['Assignee'].tolist()})  # Enforce order

                            # Update layout for better spacing and presentation
                            fig.update_traces(width=0.4)
                            fig.update_layout(
                                xaxis_title='Assignee',
                                yaxis_title='Total Weights',
                                showlegend=True,
                                xaxis={
                                    'title_standoff': 25,  # Increased spacing for x-axis title
                                    'automargin': True,     # Prevent title cutoff
                                    'categoryorder': 'total descending'  # Alternative sorting method
                                },
                                margin=dict(l=50, r=50, b=100, t=50),  # Increased bottom margin
                                uniformtext_minsize=8,  # Ensure text fits
                                uniformtext_mode='hide'  # Hide text if doesn't fit
                            )

                            st.plotly_chart(fig, use_container_width=True)

                        # Second row: Brand vs Count and Brand vs Weights by Assignee
                        col1, col2 = st.columns(2)

                        with col1:
                            st.markdown("<h5 style='text-align: center;'>Brand Distribution by Assignee</h5>", unsafe_allow_html=True)
                            if not df_non_internal.empty:
                                # Get data and sort by Count in descending order
                                brand_counts = df_non_internal.groupby(['Brand', 'Assignee Name']).size().reset_index(name='Count')
                                brand_counts['Assignee Name'] = brand_counts['Assignee Name'].apply(format_display_name)
                                brand_counts =  brand_counts.rename(columns={'Assignee Name': 'Assignee'})
                                # Sort by total count per brand (descending)
                                brand_order = brand_counts.groupby('Brand')['Count'].sum().sort_values(ascending=False).index
                                brand_counts['Brand'] = pd.Categorical(brand_counts['Brand'], categories=brand_order, ordered=True)
                                brand_counts = brand_counts.sort_values('Brand')

                                fig = px.bar(brand_counts,
                                            x='Brand',
                                            y='Count',
                                            color='Assignee',
                                            color_discrete_sequence=px.colors.qualitative.Set2,
                                            category_orders={'Brand': brand_order.tolist()})

                                fig.update_layout(
                                    barmode='group',
                                    xaxis_title='Brand',
                                    yaxis_title='Task Count',
                                    xaxis={
                                        'categoryorder': 'array',
                                        'categoryarray': brand_order,
                                        'title_standoff': 25,
                                        'automargin': True,
                                        'tickangle': 45 if len(brand_order) > 5 else 0  # Rotate if many brands
                                    },
                                    showlegend=True,
                                    margin=dict(l=50, r=50, b=150, t=50),  # Increased bottom margin
                                )
                                st.plotly_chart(fig, use_container_width=True)
                            else:
                                fig = go.Figure()
                                fig.update_layout(
                                    title='No brand data available',
                                    margin=dict(l=20, r=20, t=30, b=20)
                                )
                                st.plotly_chart(fig, use_container_width=True)

                        with col2:
                            st.markdown("<h5 style='text-align: center;'>Brand vs Weights by Assignee</h5>", unsafe_allow_html=True)
                            if not df_non_internal.empty:
                                # Get data and sort by Average in descending order
                                brand_weights = df_non_internal.groupby(['Brand', 'Assignee Name'])['Average'].sum().reset_index()
                                brand_weights['Assignee Name'] = brand_weights['Assignee Name'].apply(format_display_name)
                                brand_weights = brand_weights.rename(columns={'Assignee Name': 'Assignee'})
                                # Sort by total weight per brand (descending)
                                brand_order = brand_weights.groupby('Brand')['Average'].sum().sort_values(ascending=False).index
                                brand_weights['Brand'] = pd.Categorical(brand_weights['Brand'], categories=brand_order, ordered=True)
                                brand_weights = brand_weights.sort_values('Brand')

                                fig = px.bar(brand_weights,
                                            x='Brand',
                                            y='Average',
                                            color='Assignee',
                                            color_discrete_sequence=px.colors.qualitative.Set2,
                                            category_orders={'Brand': brand_order.tolist()})

                                fig.update_layout(
                                    barmode='group',
                                    xaxis_title='Brand',
                                    yaxis_title='Total Weight',
                                    xaxis={
                                        'categoryorder': 'array',
                                        'categoryarray': brand_order,
                                        'title_standoff': 25,
                                        'automargin': True,
                                        'tickangle': 45 if len(brand_order) > 5 else 0  # Rotate if many brands
                                    },
                                    showlegend=True,
                                    margin=dict(l=50, r=50, b=150, t=50),  # Increased bottom margin
                                )
                                st.plotly_chart(fig, use_container_width=True)
                            else:
                                fig = go.Figure()
                                fig.update_layout(
                                    title='No brand data available',
                                    margin=dict(l=20, r=20, t=30, b=20)
                                )
                                st.plotly_chart(fig, use_container_width=True)

                        st.markdown("<br><br>", unsafe_allow_html=True)

                        # Third row: Done and Pending Tasks by Assignee (percentage)
                        col1, col2 = st.columns(2)

                        with col1:
                            st.markdown("<h5 style='text-align: center;'>Done Tasks by Assignee (%)</h5>", unsafe_allow_html=True)
                            done_counts = filtered_df[filtered_df['Status'].str.lower() == 'done']
                            if not done_counts.empty:
                                done_counts = done_counts['Assignee Name'].value_counts(normalize=True).mul(100).reset_index()
                                done_counts.columns = ['Assignee', 'Percentage']
                                done_counts['Assignee'] = done_counts['Assignee'].apply(format_display_name)
                                done_counts['Percentage'] = done_counts['Percentage'].round(2)
                                fig = px.pie(
                                    done_counts,
                                    names='Assignee',
                                    values='Percentage',
                                    hole=0.3,
                                    color_discrete_sequence=px.colors.qualitative.Pastel
                                )
                                fig.update_layout(
                                    showlegend=True,
                                    margin=dict(l=20, r=20, t=30, b=20),
                                    legend=dict(
                                        orientation="h",
                                        yanchor="bottom",
                                        y=-0.2,
                                        xanchor="center",
                                        x=0.5
                                    )
                                )
                                fig.update_traces(
                                    textinfo='label+percent+value',
                                    texttemplate='%{label}<br>%{value:.1f}%<br>'
                                )
                                st.plotly_chart(fig, use_container_width=True)
                            else:
                                fig = go.Figure()
                                fig.update_layout(
                                    title='No done tasks available',
                                    margin=dict(l=20, r=20, t=30, b=20)
                                )
                                st.plotly_chart(fig, use_container_width=True)

                        with col2:
                            st.markdown("<h5 style='text-align: center;'>Pending Tasks by Assignee (%)</h5>", unsafe_allow_html=True)
                            pend_counts = filtered_df[(filtered_df['Status'].str.lower() == 'in progress')]
                            if not pend_counts.empty:
                                pend_counts = pend_counts['Assignee Name'].value_counts(normalize=True).mul(100).reset_index()
                                pend_counts.columns = ['Assignee', 'Percentage']
                                pend_counts['Assignee'] = pend_counts['Assignee'].apply(format_display_name)
                                pend_counts['Percentage'] = pend_counts['Percentage'].round(2)
                                fig = px.pie(
                                    pend_counts,
                                    names='Assignee',
                                    values='Percentage',
                                    hole=0.3,
                                    color_discrete_sequence=px.colors.qualitative.Pastel
                                )
                                fig.update_layout(
                                    showlegend=True,
                                    margin=dict(l=20, r=20, t=30, b=20),
                                    legend=dict(
                                        orientation="h",
                                        yanchor="bottom",
                                        y=-0.2,
                                        xanchor="center",
                                        x=0.5
                                    )
                                )
                                fig.update_traces(
                                    textinfo='label+percent+value',
                                    texttemplate='%{label}<br>%{value:.1f}%<br>'
                                )
                                st.plotly_chart(fig, use_container_width=True)
                            else:
                                fig = go.Figure()
                                fig.update_layout(
                                    title='No pending tasks available',
                                    margin=dict(l=20, r=20, t=30, b=20)
                                )
                                st.plotly_chart(fig, use_container_width=True)

                        st.markdown("<br><br>", unsafe_allow_html=True)

                        # Fourth row: Justifications and SLA Completion by Assignee
                        col1, col2 = st.columns(2)

                        with col1:
                            st.markdown("<h5 style='text-align: center;'>Justifications by Assignee</h5>", unsafe_allow_html=True)
                            just_counts = filtered_df[filtered_df['Justification'].str.lower() != 'none']
                            if not just_counts.empty:
                                # Get data and sort by Count in descending order
                                just_counts = just_counts['Assignee Name'].value_counts().reset_index()
                                just_counts.columns = ['Assignee', 'Count']
                                just_counts['Assignee'] = just_counts['Assignee'].apply(format_display_name)
                                just_counts = just_counts.sort_values('Count', ascending=False)  # Sort descending

                                fig = px.bar(just_counts,
                                            x='Assignee',
                                            y='Count',
                                            color='Assignee',
                                            text_auto=True,
                                            color_discrete_sequence=px.colors.qualitative.Pastel,
                                            category_orders={"Assignee": just_counts['Assignee'].tolist()})

                                fig.update_traces(width=0.4)
                                fig.update_layout(
                                    xaxis_title='Assignee',
                                    yaxis_title='Number of Justifications',
                                    showlegend=True,
                                    xaxis={
                                        'title_standoff': 25,
                                        'automargin': True,
                                        'categoryorder': 'total descending'
                                    },
                                    margin=dict(l=50, r=50, b=100, t=50),  # Increased margins
                                    uniformtext_minsize=8,
                                    uniformtext_mode='hide',
                                )
                                st.plotly_chart(fig, use_container_width=True)
                            else:
                                fig = go.Figure()
                                fig.update_layout(
                                    title='No justifications available',
                                    margin=dict(l=20, r=20, t=30, b=20)
                                )
                                st.plotly_chart(fig, use_container_width=True)

                        with col2:
                            st.markdown("<h5 style='text-align: center;'>SLA Completion by Assignee (%)</h5>", unsafe_allow_html=True)
                            sla_df = filtered_df[
                                (filtered_df['Status'].str.lower() == 'done') &
                                (filtered_df['Finished within SLA'].str.lower().isin(['yes', 'no']))
                            ]
                            if not sla_df.empty:
                                # Get data and sort by SLA Completion in descending order
                                sla_by_assignee = sla_df.groupby('Assignee Name')['Finished within SLA'].apply(
                                    lambda x: (x.str.lower() == 'yes').mean() * 100
                                ).reset_index()
                                sla_by_assignee.columns = ['Assignee', 'SLA Completion (%)']
                                sla_by_assignee['Assignee'] = sla_by_assignee['Assignee'].apply(format_display_name)
                                sla_by_assignee['SLA Completion (%)'] = sla_by_assignee['SLA Completion (%)'].astype(int)
                                sla_by_assignee = sla_by_assignee.sort_values('SLA Completion (%)', ascending=False)  # Sort descending

                                fig = px.bar(sla_by_assignee,
                                            x='Assignee',
                                            y='SLA Completion (%)',
                                            color='Assignee',
                                            text_auto=True,
                                            color_discrete_sequence=px.colors.qualitative.Pastel,
                                            category_orders={"Assignee": sla_by_assignee['Assignee'].tolist()})

                                fig.update_traces(width=0.4)
                                fig.update_layout(
                                    yaxis_range=[0, 100],
                                    showlegend=True,
                                    xaxis={
                                        'title_standoff': 25,
                                        'automargin': True,
                                        'categoryorder': 'total descending'
                                    },
                                    margin=dict(l=50, r=50, b=100, t=50),  # Increased margins
                                    uniformtext_minsize=8,
                                    uniformtext_mode='hide'

                                )
                                st.plotly_chart(fig, use_container_width=True)
                            else:
                                fig = go.Figure()
                                fig.update_layout(
                                    title='No SLA data available',
                                    margin=dict(l=20, r=20, t=30, b=20)
                                )
                                st.plotly_chart(fig, use_container_width=True)

                        # Timeline for multiple assignees
                        filtered_df['Month'] = pd.Categorical(filtered_df['Month'], categories=months, ordered=True)
                        filtered_df['Month_Num'] = filtered_df['Month'].apply(lambda x: months.index(x) + 1 if x in months else None)
                        filtered_df['Date'] = pd.to_datetime(
                            filtered_df[['Year', 'Month_Num']].dropna().astype(int).rename(columns={'Year': 'year', 'Month_Num': 'month'}).assign(day=1))
                        timeline_df = filtered_df.dropna(subset=['Date'])

                        if not timeline_df.empty:
                            st.markdown("<br><br>", unsafe_allow_html=True)
                            st.markdown("<h5 style='text-align: center;'>Task Count Over Months by Assignee</h5>", unsafe_allow_html=True)
                            timeline_tasks = timeline_df.groupby(['Date', 'Assignee Name']).size().reset_index(name='Task Count')
                            timeline_tasks['Assignee Name'] = timeline_tasks['Assignee Name'].apply(format_display_name)
                            fig = px.line(timeline_tasks, x='Date', y='Task Count', color='Assignee Name',
                                         color_discrete_sequence=px.colors.qualitative.Pastel)
                            fig.update_layout(
                                xaxis_title='Month',
                                yaxis_title='Number of Tasks',
                                showlegend=True,
                                margin=dict(l=20, r=20, t=30, b=20)
                            )
                            st.plotly_chart(fig, use_container_width=True)

                            st.markdown("<br><br>", unsafe_allow_html=True)
                            st.markdown("<h5 style='text-align: center;'>Weight Sum Over Months by Assignee</h5>", unsafe_allow_html=True)
                            timeline_weights = timeline_df.groupby(['Date', 'Assignee Name'])['Average'].sum().reset_index(name='Total Weight')
                            timeline_weights['Assignee Name'] = timeline_weights['Assignee Name'].apply(format_display_name)
                            fig = px.line(timeline_weights, x='Date', y='Total Weight', color='Assignee Name',
                                         color_discrete_sequence=px.colors.qualitative.Pastel)
                            fig.update_layout(
                                xaxis_title='Month',
                                yaxis_title='Total Weight',
                                showlegend=True,
                                margin=dict(l=20, r=20, t=30, b=20)
                            )
                            st.plotly_chart(fig, use_container_width=True)

                # Footer
                logo_url = "#"
                st.markdown(
                f"""
                <div style='text-align: center; margin-top: 50px;'>
                <a href="#" target="_blank">
                    <img src={logo_url}"  width="120" style="margin-bottom: 10px;" />
                </a>
                    <h4 style='font-size: 16px;'>📌 Authority : <a href="mailto:omarelshaarawy909@gmail.com"><b>Omar Shaarawy</b></a> | Version 2.0.0 </h4>
                </div>
                """,
                unsafe_allow_html=True
                )
            else:
                st.warning("The uploaded files could not be processed. Please check the file format.")
        else:
            st.info("Upload CSV files to analyse the data.")