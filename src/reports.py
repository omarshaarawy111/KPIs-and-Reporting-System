# Report generation functions
import pandas as pd
import numpy as np
import base64
import math
from datetime import datetime

try:
    from .visualizations import plot_to_html, generate_visualizations_html
    from .data_processing import format_display_name
except ImportError:
    from visualizations import plot_to_html, generate_visualizations_html
    from data_processing import format_display_name

def create_download_link(val, filename, file_type):
    if file_type == 'html':
        b64 = base64.b64encode(val.encode()).decode()
        return f'<a href="data:application/octet-stream;base64,{b64}" download="{filename}.html">Download HTML Report</a>'

def generate_html_report(filtered_df, df_non_internal, assignee, month, year, show_data, show_done, show_pending, show_justification, week):
    # Create report name parts
    assignee_names = "+".join([format_display_name(name) for name in assignee]) if assignee  else "All team"
    assignee_names_format = "All_Team" if not assignee or len(assignee) == 5 else "+".join([format_display_name(name) for name in assignee])
    month_names = "+".join(month) if month else "All months"
    month_names_format = "+".join(month) if month else "All_Months"
    year_names = "+".join(map(str, year)) if year else "All years"
    year_names_format = "+".join(map(str, year)) if year else "All_Years"
    week_names = "+".join(week) if week else "All weeks"
    week_names_format = "+".join(week) if week else "All_Weeks"
    report_name = f"{assignee_names_format}_{month_names_format}_{year_names_format}_{week_names_format}_Report"

    # Calculate metrics
    total_tasks = filtered_df['Task Name'].shape[0]
    total_weights = int(filtered_df['Average'].sum())
    filtered_df_sla = filtered_df[
        (filtered_df['Status'].str.lower() == 'done') &
        (filtered_df['Finished within SLA'].str.lower().isin(['yes', 'no']))
    ]
    sla_ratio = (filtered_df_sla['Finished within SLA'].str.lower() == 'yes').mean() * 100
    sla_ratio_ceil = math.ceil(sla_ratio) if not np.isnan(sla_ratio) else 0
    task_average_size = np.round(int(filtered_df['Average'].sum()) / filtered_df['Task Name'].shape[0],1)
    external_tasks = filtered_df[filtered_df['Brand'].str.lower().str.startswith('external_')]
    total_tasks_external = external_tasks['Brand'].nunique()
    total_brands = df_non_internal['Brand'].nunique() if not df_non_internal.empty else 0
    total_done = filtered_df[filtered_df['Status'].str.lower() == 'done'].shape[0]
    total_pending = filtered_df[
        (filtered_df['Status'].str.lower() == 'in progress')].shape[0]
    total_justifications = filtered_df[filtered_df['Justification'].str.lower() != 'none'].shape[0]

    # Determine if single assignee or multiple
    is_single_assignee = len(assignee) == 1 if assignee else True

    # Generate visualizations
    visuals_html = generate_visualizations_html(filtered_df, df_non_internal, is_single_assignee, assignee)

    # Start building HTML
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Metrics Monitor Report</title>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 20px;
                color: #333;
            }}
            .header {{
                background-color: #005ca1;
                color: white;
                padding: 15px;
                text-align: center;
                margin-bottom: 20px;
                border-radius: 5px;
            }}
            .report-details {{
                text-align: center;
                margin-bottom: 30px;
                font-size: 14px;
                color: #555;
            }}
            .section-title {{
                color: #005ca1;
                border-bottom: 2px solid #005ca1;
                padding-bottom: 5px;
                margin-top: 30px;
                margin-bottom: 15px;
            }}
            .metrics-grid {{
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 15px;
                margin-bottom: 30px;
            }}
            .metric-card {{
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 15px;
                text-align: center;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }}
            .metric-title {{
                font-weight: bold;
                color: #005ca1;
                margin-bottom: 10px;
            }}
            .metric-value {{
                font-size: 24px;
                font-weight: bold;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 20px;
            }}
            th {{
                background-color: #e6e6e6;
                text-align: left;
                padding: 8px;
                border: 1px solid #ddd;
            }}
            .brand-table th {{
                background-color: #005ca1;
                color: white;
            }}
            td {{
                padding: 8px;
                border: 1px solid #ddd;
            }}
            tr:nth-child(even) {{
                background-color: #f9f9f9;
            }}
            .footer {{
                margin-top: 50px;
                text-align: center;
                font-size: 12px;
                color: #005ca1;
            }}
            .comparison-section {{
                margin-top: 40px;
            }}
            .comparison-grid {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
            }}
            .comparison-table {{
                margin-bottom: 30px;
            }}
            .visualization {{
                margin: 30px 0;
                border: 1px solid #eee;
                padding: 15px;
                border-radius: 5px;
            }}
            .visualization-title {{
                text-align: center;
                font-weight: bold;
                margin-bottom: 15px;
                color: #005ca1;
            }}
            .two-columns {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
            }}
            .chart-container {{
                width: 100%;
                height: 480px;
            }}
            .break-space {{
                margin-bottom: 50px;
            }}
            .comparison-table table {{
                width: 100%;
                margin-bottom: 20px;
            }}
            .comparison-table th {{
                background-color: #005ca1;
                color: white;
                text-align: center;
            }}
            .comparison-table td {{
                text-align: center;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Metrics Monitor Report</h1>
        </div>

        <div class="report-details">
            <p><strong>Generated on:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><strong>Assignee:</strong> {assignee_names.replace('+', ', ')}</p>
            <p><strong>Month:</strong> {month_names.replace('+', ', ')}</p>
            <p><strong>Year:</strong> {year_names.replace('+', ', ')}</p>
            <p><strong>Week:</strong> {week_names.replace('+', ', ')}</p>
        </div>

        <h2 class="section-title">Key Metrics</h2>
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-title">Total Tasks</div>
                <div class="metric-value">{total_tasks}</div>
            </div>
            <div class="metric-card">
                <div class="metric-title">Total Weights</div>
                <div class="metric-value">{total_weights}</div>
            </div>
            <div class="metric-card">
                <div class="metric-title">SLA Completion</div>
                <div class="metric-value">{sla_ratio_ceil}%</div>
            </div>
            <div class="metric-card">
                <div class="metric-title">Task Average Size</div>
                <div class="metric-value">{task_average_size}</div>
            </div>
            <div class="metric-card">
                <div class="metric-title">External Missions</div>
                <div class="metric-value">{total_tasks_external}</div>
            </div>
            <div class="metric-card">
                <div class="metric-title">Total Brands</div>
                <div class="metric-value">{total_brands}</div>
            </div>
            <div class="metric-card">
                <div class="metric-title">Done Tasks</div>
                <div class="metric-value">{total_done}</div>
            </div>
            <div class="metric-card">
                <div class="metric-title">Pending Tasks</div>
                <div class="metric-value">{total_pending}</div>
            </div>
            <div class="metric-card">
                <div class="metric-title">Justifications</div>
                <div class="metric-value">{total_justifications}</div>
            </div>
        </div>
    """

    # Add assignee comparison section if multiple assignees
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
            html += """
        <div class="comparison-section">
            <h2 class="section-title">Assignee Comparison</h2>
        """
            assignee_df_stats = pd.DataFrame(assignee_stats)

            # Champion table (Total Weights)
            champion_table = assignee_df_stats.sort_values('Total Weights', ascending=False).reset_index(drop=True)
            champion_table = champion_table[['Assignee', 'Total Weights']]

            html += """
            <div class="comparison-table">
                <h3>Champion Table (Total Weights)</h3>
                <table>
                    <thead>
                        <tr>
                            <th>Assignee</th>
                            <th>Total Weights</th>
                        </tr>
                    </thead>
                    <tbody>
            """
            for _, row in champion_table.iterrows():
                html += f"""
                        <tr>
                            <td>{row['Assignee']}</td>
                            <td>{row['Total Weights']}</td>
                        </tr>
                """
            html += """
                    </tbody>
                </table>
            </div>
            """

            # Detailed metrics table
            detailed_metrics = assignee_df_stats[['Assignee', 'Total Tasks', 'SLA Completion',
                                               'Task Average Size', 'External Missions', 'Total Brands',
                                               'Done Tasks', 'Pending Tasks', 'Justifications']]

            html += """
            <div class="comparison-table">
                <h3>Detailed Assignee Metrics</h3>
                <table>
                    <thead>
                        <tr>
                            <th>Assignee</th>
                            <th>Total Tasks</th>
                            <th>SLA Completion</th>
                            <th>Task Average Size</th>
                            <th>External Missions</th>
                            <th>Total Brands</th>
                            <th>Done Tasks</th>
                            <th>Pending Tasks</th>
                            <th>Justifications</th>
                        </tr>
                    </thead>
                    <tbody>
            """
            for _, row in detailed_metrics.iterrows():
                html += f"""
                        <tr>
                            <td>{row['Assignee']}</td>
                            <td>{row['Total Tasks']}</td>
                            <td>{row['SLA Completion']}%</td>
                            <td>{row['Task Average Size']}</td>
                            <td>{row['External Missions']}</td>
                            <td>{row['Total Brands']}</td>
                            <td>{row['Done Tasks']}</td>
                            <td>{row['Pending Tasks']}</td>
                            <td>{row['Justifications']}</td>
                </tr>
                """
            html += """
                    </tbody>
                </table>
            </div>
            """

            html += "</div>"  # Close comparison-section
    html += f"""
        <h2 class="section-title">Visualizations</h2>
        {visuals_html}

        <h2 class="section-title">Data Tables</h2>
    """

    # Function to add dataframe to HTML
    def add_dataframe_to_html(df, title, justification_table=False, all_data_table=False, brand_table=False):
        if df.empty:
            return f"<p><em>No data available for {title}</em></p>"

        # Create a copy of the dataframe for display
        display_df = df.copy()
        if 'Assignee Name' in display_df.columns:
            display_df['Assignee Name'] = display_df['Assignee Name'].apply(format_display_name)

        # Rename 'Finished within SLA' to 'SLA' and 'Assignee Name' to 'Assignee'
        if 'Finished within SLA' in display_df.columns:
            display_df = display_df.rename(columns={'Finished within SLA': 'SLA'})
        if 'Assignee Name' in display_df.columns:
            display_df = display_df.rename(columns={'Assignee Name': 'Assignee'})

        # Define columns for each table type with specified order
        if all_data_table:
            columns = [
                'Assignee', 'Task Name', 'Brand', 'Priority',
                'SLA', 'Average', 'Status', 'Month', 'Year'
            ]
        elif justification_table:
            columns = [
                'Assignee', 'Task Name', 'Justification', 'Brand',
                'Priority', 'SLA', 'Average', 'Month', 'Year'
            ]
        elif brand_table:
            columns = ['Brand', 'Task Name', 'Assignee', 'Priority', 'SLA', 'Average', 'Status', 'Month', 'Year']
        else:
            columns = [
                'Assignee', 'Task Name', 'Brand', 'Priority',
                'SLA', 'Average', 'Month', 'Year'
            ]

        # Filter only existing columns
        display_cols = [col for col in columns if col in display_df.columns]
        df_display = display_df[display_cols].copy()

        # Convert average to int if it exists
        if 'Average' in df_display.columns:
            df_display['Average'] = df_display['Average'].astype(int)

        # Remove Month/Year columns if single month/year selected
        if len(month) == 1 and 'Month' in df_display.columns:
            df_display = df_display.drop(columns=['Month'])
        if len(year) == 1 and 'Year' in df_display.columns:
            df_display = df_display.drop(columns=['Year'])

        # Sort by Year, Month if available
        if 'Year' in df_display.columns and 'Month' in df_display.columns:
            months_order = ["January", "February", "March", "April", "May", "June",
                          "July", "August", "September", "October", "November", "December"]
            df_display['Month'] = pd.Categorical(df_display['Month'], categories=months_order, ordered=True)
            df_display = df_display.sort_values(['Year', 'Month'])
            df_display['Year'] = df_display['Year'].astype(int)

        # Generate HTML table
        table_class = 'data-table brand-table' if brand_table else 'data-table'
        table_html = f"""
        <h3>{title}</h3>
        {df_display.to_html(index=False, classes=table_class)}
        """

        return table_html

    # Add tables
    if is_single_assignee:
        html += add_dataframe_to_html(filtered_df, "Task Distribution by Brands", brand_table=True)
        html += add_dataframe_to_html(filtered_df, "Weights per Brand", brand_table=True)
    html += add_dataframe_to_html(filtered_df, "All Data", all_data_table=True)

    done_df = filtered_df[filtered_df['Status'].str.lower() == 'done']
    html += add_dataframe_to_html(done_df, "Done Tasks")

    pend_df = filtered_df[
        (filtered_df['Status'].str.lower() == 'in progress')
    ]
    html += add_dataframe_to_html(pend_df, "Pending Tasks")

    just_df = filtered_df[filtered_df['Justification'].str.lower() != 'none']
    html += add_dataframe_to_html(just_df, "All Justifications", justification_table=True)

    # Add footer
    html += """
    <div class="footer">

        <p>🚀 Generated by Web & Search Team - NBS Cairo</p>
        <p>📌 Authority : Omar Shaarawy | Version 2.0.0 </p>



    </div>
    </body>
    </html>
    """

    return html, report_name