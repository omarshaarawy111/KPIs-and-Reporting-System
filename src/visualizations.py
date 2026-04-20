# Visualization functions
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

try:
    from .data_processing import format_display_name
except ImportError:
    from data_processing import format_display_name

def plot_to_html(fig):
    return fig.to_html(full_html=False, include_plotlyjs='cdn')

def generate_visualizations_html(filtered_df, df_non_internal, is_single_assignee, assignee):
    months = ["January", "February", "March", "April", "May", "June",
              "July", "August", "September", "October", "November", "December"]

    visuals_html = ""

    if not filtered_df.empty:
        if is_single_assignee or len(assignee) == 1:
            # Single assignee visuals (same as web page)
            visuals_html += "<div class='two-columns'>"

            # Task Distribution by Brands
            if not df_non_internal.empty:
                fig = px.histogram(df_non_internal, x='Brand', color='Brand', text_auto=True,
                  color_discrete_sequence=px.colors.qualitative.Pastel)
                fig.update_layout(
                    xaxis=dict(
                        categoryorder='total descending',
                        title_text='Brands',
                        title_standoff=30,
                        automargin=True,
                        title_font=dict(size=14),
                    ),
                    margin=dict(l=50, r=50, b=120, t=50, pad=10),
                    xaxis_title_font=dict(size=14)  # Explicitly set title font
                )
                visuals_html += f"""
                <div class="visualization">
                    <div class="visualization-title">Task Distribution by Brands</div>
                    <div class="chart-container">{plot_to_html(fig)}</div>
                </div>
                """
            else:
                fig = go.Figure()
                fig.update_layout(
                    xaxis=dict(
                        categoryorder='total descending',
                        title_text='Brands',
                        title_standoff=30,
                        automargin=True,
                        title_font=dict(size=14),
                    ),
                    margin=dict(l=50, r=50, b=120, t=50, pad=10),
                    xaxis_title_font=dict(size=14)  # Explicitly set title font
                )
                fig.add_annotation(text="No brand data available", xref="paper", yref="paper",
                                 x=0.5, y=0.5, showarrow=False)
                visuals_html += f"""
                <div class="visualization">
                    <div class="visualization-title">Task Distribution by Brands</div>
                    <div class="chart-container">{plot_to_html(fig)}</div>
                </div>
                """

            # Weights per Brand
            if not df_non_internal.empty:
                fig = px.histogram(df_non_internal, x='Brand', y='Average', color='Brand', text_auto=True,
                                 color_discrete_sequence=px.colors.qualitative.Pastel)
                fig.update_layout(
                    xaxis=dict(
                        categoryorder='total descending',
                        title_text='Brands',
                        title_standoff=30,
                        automargin=True,
                        title_font=dict(size=14),
                    ),
                    margin=dict(l=50, r=50, b=120, t=50, pad=10),
                    xaxis_title_font=dict(size=14),  # Explicitly set title font
                    yaxis=dict(
                        title_text='Weights',
                        automargin=True,
                        title_font=dict(size=14),
                    )
                )
                visuals_html += f"""
                <div class="visualization">
                    <div class="visualization-title">Weights per Brand</div>
                    <div class="chart-container">{plot_to_html(fig)}</div>
                </div>
                """
            else:
                fig = go.Figure()
                fig.update_layout(
                    xaxis=dict(
                        categoryorder='total descending',
                        title_text='Brands',
                        title_standoff=30,
                        automargin=True,
                        title_font=dict(size=14),
                    ),
                    margin=dict(l=50, r=50, b=120, t=50, pad=10),
                    xaxis_title_font=dict(size=14),  # Explicitly set title font
                    yaxis=dict(
                        title_text='Weights',
                        automargin=True,
                        title_font=dict(size=14),
                    )
                )
                fig.add_annotation(text="No brand data available", xref="paper", yref="paper",
                                 x=0.5, y=0.5, showarrow=False)
                visuals_html += f"""
                <div class="visualization">
                    <div class="visualization-title">Weights per Brand</div>
                    <div class="chart-container">{plot_to_html(fig)}</div>
                </div>
                """

            visuals_html += "</div>"  # Close two-columns

            # Task Distribution by Priority and SLA Completion
            visuals_html += "<div class='two-columns'>"

            # Task Distribution by Priority (%)
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
                visuals_html += f"""
                <div class="visualization">
                    <div class="visualization-title">Task Distribution by Priority (%)</div>
                    <div class="chart-container">{plot_to_html(fig)}</div>
                </div>
                """
            else:
                fig = go.Figure()
                fig.update_layout(margin=dict(l=20, r=20, t=30, b=20))
                fig.add_annotation(text="No priority data available", xref="paper", yref="paper",
                                 x=0.5, y=0.5, showarrow=False)
                visuals_html += f"""
                <div class="visualization">
                    <div class="visualization-title">Task Distribution by Priority (%)</div>
                    <div class="chart-container">{plot_to_html(fig)}</div>
                </div>
                """

            # SLA Completion (%)
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
                visuals_html += f"""
                <div class="visualization">
                    <div class="visualization-title">SLA Completion (%)</div>
                    <div class="chart-container">{plot_to_html(fig)}</div>
                </div>
                """
            else:
                fig = go.Figure()
                fig.update_layout(margin=dict(l=20, r=20, t=30, b=20))
                fig.add_annotation(text="No SLA data available", xref="paper", yref="paper",
                                 x=0.5, y=0.5, showarrow=False)
                visuals_html += f"""
                <div class="visualization">
                    <div class="visualization-title">SLA Completion (%)</div>
                    <div class="chart-container">{plot_to_html(fig)}</div>
                </div>
                """

            visuals_html += "</div>"  # Close two-columns

            # Dev Agency Work and Task Completion
            visuals_html += "<div class='two-columns'>"

            # Dev Agency Work
            filtered_df_dev = filtered_df[filtered_df['Dev Agency Contribution'].str.lower().isin(['yes', 'no'])]
            if not filtered_df_dev.empty:
                fig = px.histogram(filtered_df_dev, x='Dev Agency Contribution', color='Dev Agency Contribution',
                                 color_discrete_map={'No': 'green', 'Yes': 'red'}, text_auto=True)
                fig.update_layout(
                    xaxis=dict(
                        categoryorder='total descending',
                        title_text='Dev Agency Contribution',
                        title_standoff=30,
                        automargin=True,
                        title_font=dict(size=14),
                    ),
                    margin=dict(l=50, r=50, b=120, t=50, pad=10),
                    xaxis_title_font=dict(size=14),  # Explicitly set title font
                )
                visuals_html += f"""
                <div class="visualization">
                    <div class="visualization-title">Dev Agency Work</div>
                    <div class="chart-container">{plot_to_html(fig)}</div>
                </div>
                """
            else:
                fig = go.Figure()
                fig.update_layout(
                    xaxis=dict(
                        categoryorder='total descending',
                        title_text='Dev Agency Contribution',
                        title_standoff=30,
                        automargin=True,
                        title_font=dict(size=14),
                    ),
                    margin=dict(l=50, r=50, b=120, t=50, pad=10),
                    xaxis_title_font=dict(size=14),  # Explicitly set title font
                )
                fig.add_annotation(text="No Dev Agency data available", xref="paper", yref="paper",
                                 x=0.5, y=0.5, showarrow=False)
                visuals_html += f"""
                <div class="visualization">
                    <div class="visualization-title">Dev Agency Work</div>
                    <div class="chart-container">{plot_to_html(fig)}</div>
                </div>
                """

            # Task Completion (%)
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
                visuals_html += f"""
                <div class="visualization">
                    <div class="visualization-title">Task Completion (%)</div>
                    <div class="chart-container">{plot_to_html(fig)}</div>
                </div>
                """
            else:
                fig = go.Figure()
                fig.update_layout(margin=dict(l=20, r=20, t=30, b=20))
                fig.add_annotation(text="No status data available", xref="paper", yref="paper",
                                 x=0.5, y=0.5, showarrow=False)
                visuals_html += f"""
                <div class="visualization">
                    <div class="visualization-title">Task Completion (%)</div>
                    <div class="chart-container">{plot_to_html(fig)}</div>
                </div>
                """

            visuals_html += "</div>"  # Close two-columns

            # Timeline
            filtered_df['Month'] = pd.Categorical(filtered_df['Month'], categories=months, ordered=True)
            filtered_df['Month_Num'] = filtered_df['Month'].apply(lambda x: months.index(x) + 1 if x in months else None)
            filtered_df['Date'] = pd.to_datetime(
                filtered_df[['Year', 'Month_Num']].dropna().astype(int).rename(columns={'Year': 'year', 'Month_Num': 'month'}).assign(day=1))
            timeline_df = filtered_df.dropna(subset=['Date'])

            if not timeline_df.empty:
                # Task Count Over Months
                timeline_tasks = timeline_df.groupby('Date').size().reset_index(name='Task Count')
                fig = px.line(timeline_tasks, x='Date', y='Task Count', markers=True,
                             color_discrete_sequence=['#7fc7fc'])
                fig.update_layout(
                    xaxis_title='Month',
                    yaxis_title='Number of Tasks',
                    margin=dict(l=20, r=20, t=30, b=20)
                )
                visuals_html += f"""
                <div class="visualization">
                    <div class="visualization-title">Task Count Over Months</div>
                    <div class="chart-container">{plot_to_html(fig)}</div>
                    <br><br>
                </div>
                """

                # Weight Sum Over Months
                timeline_weights = timeline_df.groupby('Date')['Average'].sum().reset_index(name='Total Weight')
                fig = px.line(timeline_weights, x='Date', y='Total Weight', markers=True,
                             color_discrete_sequence=['#7fc7fc'])
                fig.update_layout(
                    xaxis_title='Month',
                    yaxis_title='Total Weight',
                    margin=dict(l=20, r=20, t=30, b=20)
                )
                visuals_html += f"""
                <div class="visualization">
                    <div class="visualization-title">Weight Sum Over Months</div>
                    <div class="chart-container">{plot_to_html(fig)}</div>
                </div>
                """
            else:
                # Empty timeline placeholders
                fig = go.Figure()
                fig.update_layout(
                    xaxis_title='Month',
                    yaxis_title='Number of Tasks',
                    margin=dict(l=20, r=20, t=30, b=20)
                )
                fig.add_annotation(text="No timeline data available", xref="paper", yref="paper",
                                 x=0.5, y=0.5, showarrow=False)
                visuals_html += f"""
                <div class="visualization">
                    <div class="visualization-title">Task Count Over Months</div>
                    <div class="chart-container">{plot_to_html(fig)}</div>
                </div>
                """

                fig = go.Figure()
                fig.update_layout(
                    xaxis_title='Month',
                    yaxis_title='Total Weight',
                    margin=dict(l=20, r=20, t=30, b=20)
                )
                fig.add_annotation(text="No timeline data available", xref="paper", yref="paper",
                                 x=0.5, y=0.5, showarrow=False)
                visuals_html += f"""
                <div class="visualization">
                    <div class="visualization-title">Weight Sum Over Months</div>
                    <div class="chart-container">{plot_to_html(fig)}</div>
                </div>
                """

            # Add break space after timeline
            visuals_html += "<div class='break-space'></div>"

        else:
            # Multiple assignees visuals - comparison mode

            # First row: Task Count and Total Weights by Assignee
            visuals_html += "<div class='two-columns'>"

            # Task Count by Assignee
            assignee_tasks = filtered_df['Assignee Name'].value_counts().reset_index()
            assignee_tasks.columns = ['Assignee', 'Task Count']
            assignee_tasks['Assignee'] = assignee_tasks['Assignee'].apply(lambda x: format_display_name(x) if pd.notna(x) else "Unknown")
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
                yaxis_title='',
                showlegend=True,
                xaxis={
                    'title_standoff': 30,  # Increased spacing for x-axis title
                    'automargin': True,     # Prevent title cutoff
                    'categoryorder': 'total descending'  # Alternative sorting method
                    },
            margin=dict(l=50, r=50, b=100, t=50),  # Increased bottom margin
            uniformtext_minsize=8,  # Ensure text fits
            uniformtext_mode='hide'  # Hide text if doesn't fit
                            )
            visuals_html += f"""
            <div class="visualization">
                <div class="visualization-title">Task Count by Assignee</div>
                <div class="chart-container">{plot_to_html(fig)}</div>
            </div>
            """

            # Total Weights by Assignee
            assignee_weights = filtered_df.groupby('Assignee Name')['Average'].sum().reset_index()
            assignee_weights.columns = ['Assignee', 'Total Weights']
            assignee_weights['Assignee'] = assignee_weights['Assignee'].apply(lambda x: format_display_name(x) if pd.notna(x) else "Unknown")
            # Create the bar chart
            fig = px.bar(assignee_weights,
                        x='Assignee',
                        y='Total Weights',
                        color='Assignee',
                        text_auto=True,
                        color_discrete_sequence=px.colors.qualitative.Pastel,
                        category_orders={"Assignee": assignee_tasks['Assignee'].tolist()})  # Enforce order

            # Update layout for better spacing and presentation
            fig.update_traces(width=0.4)
            fig.update_layout(
                        xaxis_title='Assignee',
                        yaxis_title='',
                        showlegend=True,
                        xaxis={
                            'title_standoff': 30,  # Increased spacing for x-axis title
                            'automargin': True,     # Prevent title cutoff
                            'categoryorder': 'total descending'  # Alternative sorting method
                            },
                        margin=dict(l=50, r=50, b=100, t=50),  # Increased bottom margin
                        uniformtext_minsize=8,  # Ensure text fits
                        uniformtext_mode='hide'  # Hide text if doesn't fit
                            )
            visuals_html += f"""
            <div class="visualization">
                <div class="visualization-title">Total Weights by Assignee</div>
                <div class="chart-container">{plot_to_html(fig)}</div>
            </div>
            """
            visuals_html += "</div>"  # Close two-columns

            # Second row: Brand vs Count and Brand vs Weights by Assignee
            visuals_html += "<div class='two-columns'>"

            # Brand Distribution by Assignee
            if not df_non_internal.empty:
                brand_counts = df_non_internal.groupby(['Brand', 'Assignee Name']).size().reset_index(name='Count')
                brand_counts['Assignee Name'] = brand_counts['Assignee Name'].apply(lambda x: format_display_name(x) if pd.notna(x) else "Unknown")
                brand_counts = brand_counts.rename(columns={'Assignee Name': 'Assignee'})
                fig = px.bar(brand_counts, x='Brand', y='Count', color='Assignee',
                             color_discrete_sequence=px.colors.qualitative.Set2)
                fig.update_layout(
                    barmode='group',
                    yaxis_title='',
                    showlegend=True,
                    xaxis=dict(
                    categoryorder =  'total descending',
                    title='Brand',
                    title_standoff=50,
                    automargin=True,
                    title_font=dict(size=14),
                              ),
                    margin=dict(l=20, r=20, t=30, b=20)

                )
                visuals_html += f"""
                <div class="visualization">
                    <div class="visualization-title">Brand Distribution by Assignee</div>
                    <div class="chart-container">{plot_to_html(fig)}</div>
                </div>
                """
            else:
                fig = go.Figure()
                fig.update_layout(
                    xaxis_title='Brand',
                    yaxis_title='',
                    xaxis= dict ( title_standoff = 50),
                    margin=dict(l=20, r=20, t=30, b=20)
                )
                fig.add_annotation(text="No brand data available", xref="paper", yref="paper",
                                 x=0.5, y=0.5, showarrow=False)
                visuals_html += f"""
                <div class="visualization">
                    <div class="visualization-title">Brand Distribution by Assignee</div>
                    <div class="chart-container">{plot_to_html(fig)}</div>
                </div>
                """

            # Brand vs Weights by Assignee
            if not df_non_internal.empty:
                brand_weights = df_non_internal.groupby(['Brand', 'Assignee Name'])['Average'].sum().reset_index()
                brand_weights['Assignee Name'] = brand_weights['Assignee Name'].apply(lambda x: format_display_name(x) if pd.notna(x) else "Unknown")
                brand_weights = brand_weights.rename(columns={'Assignee Name': 'Assignee'})
                fig = px.bar(brand_weights, x='Brand', y='Average', color='Assignee',
                             color_discrete_sequence=px.colors.qualitative.Set2)
                fig.update_layout(
                    barmode='group',
                    xaxis_title='Brand',
                    yaxis_title='',
                    showlegend=True,
                    xaxis=dict(
                    categoryorder =  'total descending',
                    title='Brand',
                    title_standoff=50,
                    automargin=True,
                    title_font=dict(size=14),
                              ),
                    margin=dict(l=30, r=20, t=30, b=20)
                )
                visuals_html += f"""
                <div class="visualization">
                    <div class="visualization-title">Brand vs Weights by Assignee</div>
                    <div class="chart-container">{plot_to_html(fig)}</div>
                </div>
                """
            else:
                fig = go.Figure()
                fig.update_layout(
                    xaxis_title='Brand',
                    yaxis_title='',
                    xaxis={'title_standoff': 50},
                    margin=dict(l=20, r=20, t=30, b=20)
                )
                fig.add_annotation(text="No brand data available", xref="paper", yref="paper",
                                 x=0.5, y=0.5, showarrow=False)
                visuals_html += f"""
                <div class="visualization">
                    <div class="visualization-title">Brand vs Weights by Assignee</div>
                    <div class="chart-container">{plot_to_html(fig)}</div>
                </div>
                """
            visuals_html += "</div>"  # Close two-columns

            # Third row: Done and Pending Tasks by Assignee (percentage)
            visuals_html += "<div class='two-columns'>"

            # Done Tasks by Assignee (%)
            done_counts = filtered_df[filtered_df['Status'].str.lower() == 'done']
            if not done_counts.empty:
                done_counts = done_counts['Assignee Name'].value_counts(normalize=True).mul(100).reset_index()
                done_counts.columns = ['Assignee', 'Percentage']
                done_counts['Assignee'] = done_counts['Assignee'].apply(lambda x: format_display_name(x) if pd.notna(x) else "Unknown")
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
                visuals_html += f"""
                <div class="visualization">
                    <div class="visualization-title">Done Tasks by Assignee (%)</div>
                    <div class="chart-container">{plot_to_html(fig)}</div>
                </div>
                """
            else:
                fig = go.Figure()
                fig.update_layout(margin=dict(l=20, r=20, t=30, b=20))
                fig.add_annotation(text="No done tasks available", xref="paper", yref="paper",
                                 x=0.5, y=0.5, showarrow=False)
                visuals_html += f"""
                <div class="visualization">
                    <div class="visualization-title">Done Tasks by Assignee (%)</div>
                    <div class="chart-container">{plot_to_html(fig)}</div>
                </div>
                """

            # Pending Tasks by Assignee (%)
            pend_counts = filtered_df[(filtered_df['Status'].str.lower() == 'in progress')]
            if not pend_counts.empty:
                pend_counts = pend_counts['Assignee Name'].value_counts(normalize=True).mul(100).reset_index()
                pend_counts.columns = ['Assignee', 'Percentage']
                pend_counts['Assignee'] = pend_counts['Assignee'].apply(lambda x: format_display_name(x) if pd.notna(x) else "Unknown")
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
                visuals_html += f"""
                <div class="visualization">
                    <div class="visualization-title">Pending Tasks by Assignee (%)</div>
                    <div class="chart-container">{plot_to_html(fig)}</div>
                </div>
                """
            else:
                fig = go.Figure()
                fig.update_layout(margin=dict(l=20, r=20, t=30, b=20))
                fig.add_annotation(text="No pending tasks available", xref="paper", yref="paper",
                                 x=0.5, y=0.5, showarrow=False)
                visuals_html += f"""
                <div class="visualization">
                    <div class="visualization-title">Pending Tasks by Assignee (%)</div>
                    <div class="chart-container">{plot_to_html(fig)}</div>
                </div>
                """

            visuals_html += "</div>"  # Close two-columns

            # Fourth row: Justifications and SLA Completion by Assignee
            visuals_html += "<div class='two-columns'>"

            # Justifications by Assignee
            just_counts = filtered_df[filtered_df['Justification'].str.lower() != 'none']
            if not just_counts.empty:
                just_counts = just_counts['Assignee Name'].value_counts().reset_index()
                just_counts.columns = ['Assignee', 'Count']
                just_counts['Assignee'] = just_counts['Assignee'].apply(lambda x: format_display_name(x) if pd.notna(x) else "Unknown")
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
                        yaxis_title='',
                        showlegend=True,
                        xaxis={
                            'title_standoff': 30,
                            'automargin': True,
                            'categoryorder': 'total descending'
                            },
                        margin=dict(l=50, r=50, b=100, t=50),  # Increased margins
                        uniformtext_minsize=8,
                        uniformtext_mode='hide',
                            )
                visuals_html += f"""
                <div class="visualization">
                    <div class="visualization-title">Justifications by Assignee</div>
                    <div class="chart-container">{plot_to_html(fig)}</div>
                </div>
                """
            else:
                fig = go.Figure()
                fig.update_layout(margin=dict(l=20, r=20, t=30, b=20))
                fig.add_annotation(text="No justifications available", xref="paper", yref="paper",
                                 x=0.5, y=0.5, showarrow=False)
                visuals_html += f"""
                <div class="visualization">
                    <div class="visualization-title">Justifications by Assignee</div>
                    <div class="chart-container">{plot_to_html(fig)}</div>
                </div>
                """

            # SLA Completion by Assignee (%)
            sla_df = filtered_df[
                (filtered_df['Status'].str.lower() == 'done') &
                (filtered_df['Finished within SLA'].str.lower().isin(['yes', 'no']))
            ]
            if not sla_df.empty:
                sla_by_assignee = sla_df.groupby('Assignee Name')['Finished within SLA'].apply(
                    lambda x: (x.str.lower() == 'yes').mean() * 100
                ).reset_index()
                sla_by_assignee.columns = ['Assignee', 'SLA Completion (%)']
                sla_by_assignee['Assignee'] = sla_by_assignee['Assignee'].apply(lambda x: format_display_name(x) if pd.notna(x) else "Unknown")
                sla_by_assignee['SLA Completion (%)'] = sla_by_assignee['SLA Completion (%)'].astype(int)
                fig = px.bar(sla_by_assignee,
                                            x='Assignee',
                                            y='SLA Completion (%)',
                                            color='Assignee',
                                            text_auto=True,
                                            color_discrete_sequence=px.colors.qualitative.Pastel,
                                            category_orders={"Assignee": just_counts['Assignee'].tolist()})

                fig.update_traces(width=0.4)
                fig.update_layout(
                                xaxis_title='Assignee',
                                yaxis_title='',
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
                visuals_html += f"""
                <div class="visualization">
                    <div class="visualization-title">SLA Completion by Assignee (%)</div>
                    <div class="chart-container">{plot_to_html(fig)}</div>
                </div>
                """
            else:
                fig = go.Figure()
                fig.update_layout(margin=dict(l=20, r=20, t=30, b=20))
                fig.add_annotation(text="No SLA data available", xref="paper", yref="paper",
                                 x=0.5, y=0.5, showarrow=False)
                visuals_html += f"""
                <div class="visualization">
                    <div class="visualization-title">SLA Completion by Assignee (%)</div>
                    <div class="chart-container">{plot_to_html(fig)}</div>
                </div>
                """

            visuals_html += "</div>"  # Close two-columns

            # Timeline for multiple assignees
            filtered_df['Month'] = pd.Categorical(filtered_df['Month'], categories=months, ordered=True)
            filtered_df['Month_Num'] = filtered_df['Month'].apply(lambda x: months.index(x) + 1 if x in months else None)
            filtered_df['Date'] = pd.to_datetime(
                filtered_df[['Year', 'Month_Num']].dropna().astype(int).rename(columns={'Year': 'year', 'Month_Num': 'month'}).assign(day=1))
            timeline_df = filtered_df.dropna(subset=['Date'])

            if not timeline_df.empty:
                # Task Count Over Months by Assignee
                timeline_tasks = timeline_df.groupby(['Date', 'Assignee Name']).size().reset_index(name='Task Count')
                timeline_tasks['Assignee Name'] = timeline_tasks['Assignee Name'].apply(lambda x: format_display_name(x) if pd.notna(x) else "Unknown")
                fig = px.line(timeline_tasks, x='Date', y='Task Count', color='Assignee Name',
                             color_discrete_sequence=px.colors.qualitative.Pastel)
                fig.update_layout(
                    xaxis_title='Month',
                    yaxis_title='Number of Tasks',
                    showlegend=True,
                    xaxis={'title_standoff': 50},
                    margin=dict(l=20, r=20, t=30, b=20)
                )
                visuals_html += f"""
                <div class="visualization">
                    <div class="visualization-title">Task Count Over Months by Assignee</div>
                    <div class="chart-container">{plot_to_html(fig)}</div>
                </div>
                """

                # Weight Sum Over Months by Assignee
                timeline_weights = timeline_df.groupby(['Date', 'Assignee Name'])['Average'].sum().reset_index(name='Total Weight')
                timeline_weights['Assignee Name'] = timeline_weights['Assignee Name'].apply(lambda x: format_display_name(x) if pd.notna(x) else "Unknown")
                fig = px.line(timeline_weights, x='Date', y='Total Weight', color='Assignee Name',
                              color_discrete_sequence=px.colors.qualitative.Pastel)
                fig.update_layout(
                    xaxis_title='Month',
                    yaxis_title='Total Weight',
                    showlegend=True,
                    xaxis={'title_standoff': 50},
                    margin=dict(l=20, r=20, t=30, b=20)
                )
                visuals_html += f"""
                <div class="visualization">
                    <div class="visualization-title">Weight Sum Over Months by Assignee</div>
                    <div class="chart-container">{plot_to_html(fig)}</div>
                </div>
                """
            else:
                # Empty timeline placeholders
                fig = go.Figure()
                fig.update_layout(
                    xaxis_title='Month',
                    yaxis_title='Number of Tasks',
                    xaxis={'title_standoff': 50},
                    margin=dict(l=20, r=20, t=30, b=20)
                )
                fig.add_annotation(text="No timeline data available", xref="paper", yref="paper",
                                 x=0.5, y=0.5, showarrow=False)
                visuals_html += f"""
                <div class="visualization">
                    <div class="visualization-title">Task Count Over Months by Assignee</div>
                    <div class="chart-container">{plot_to_html(fig)}</div>
                </div>
                """

                fig = go.Figure()
                fig.update_layout(
                    xaxis_title='Month',
                    yaxis_title='Total Weight',
                    xaxis={'title_standoff': 50},
                    margin=dict(l=20, r=20, t=30, b=20)
                )
                fig.add_annotation(text="No timeline data available", xref="paper", yref="paper",
                                 x=0.5, y=0.5, showarrow=False)
                visuals_html += f"""
                <div class="visualization">
                    <div class="visualization-title">Weight Sum Over Months by Assignee</div>
                    <div class="chart-container">{plot_to_html(fig)}</div>
                </div>
                """

            # Add break space after timeline
            visuals_html += "<div class='break-space'></div>"

    return visuals_html