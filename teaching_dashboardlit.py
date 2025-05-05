import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Making it pretty
subject_colors = {
    'EnglishScore': '#EF553B',
    'MathScore': '#636EFA',
    'ChemistryScore': '#00CC96',
    'PhysicsScore': '#AB63FA',
    'BiologyScore': '#FFA15A'
}

teaching_method_colors = {
    'Lecture-Based Instruction': '#636EFA',
    'Facilitator': '#EF553B',
    'Technology Based Learning': '#00CC96',
    'Group Learning': '#AB63FA',
    'Individual Learning': '#FFA15A',
    'Inquiry-Based Learning': '#19D3F3',
    'Differentiated Instruction': '#FF6692'
}

# Load data
df = pd.read_excel("teaching_data.xlsx", sheet_name='Sheet1')


# Melted data for analysis
df_melted = df.melt(id_vars=['StudentID', 'TeachingMethod'],
                    value_vars=['EnglishScore', 'MathScore', 'ChemistryScore', 'PhysicsScore', 'BiologyScore'],
                    var_name='Subject', value_name='Score')

# Summary statistics
descriptive_stats = df_melted.groupby(['TeachingMethod', 'Subject']).agg(
    Count=('Score', 'count'),
    Mean=('Score', 'mean'),
    Median=('Score', 'median'),
    Mode=('Score', lambda x: x.mode().iloc[0] if not x.mode().empty else None),
    StdDev=('Score', 'std'),
    Variance=('Score', 'var'),
    Range=('Score', lambda x: x.max() - x.min()),
    IQR=('Score', lambda x: x.quantile(0.75) - x.quantile(0.25))
).reset_index()

# Confidence Intervals
z_score = 1.96
descriptive_stats['CI'] = z_score * (descriptive_stats['StdDev'] / np.sqrt(descriptive_stats['Count']))

# Streamlit layout
st.set_page_config(layout="wide", page_title="Teaching Methods Dashboard")

st.title("📊 Teaching Methods Dashboard")
st.subheader("ESM 250 - Educational Strategy & Methodology")

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Mean ± 95% CI per Subject", "Top Performing Methods", "Overall Method Comparison",
    "Mean Scores by Subject/Method", "Statistical Summary", "Descriptive Stats Table"
])

# Tab 1 - Confidence Intervals
with tab1:
    st.header("Mean Scores ± 95% Confidence Intervals")
    for subject in df_melted['Subject'].unique():
        sub_data = descriptive_stats[descriptive_stats['Subject'] == subject]
        fig = go.Figure()
        fig.add_trace(go.Bar(
    x=sub_data['TeachingMethod'],
    y=sub_data['Mean'],
    error_y=dict(type='data', array=sub_data['CI'], visible=True),
    name=subject,
    marker_color=subject_colors.get(subject, '#CCCCCC')  # Adds subject-specific color
))
        fig.update_layout(
            title=f"{subject} - Mean Score with 95% Confidence Interval",
            xaxis_title="Teaching Method",
            yaxis_title="Score",
            template="plotly_dark"
        )
        st.plotly_chart(fig, use_container_width=True)

# Tab 2 - Top Methods
with tab2:
    st.header("Top Performing Teaching Methods by Subject")
    top_methods = descriptive_stats.loc[descriptive_stats.groupby('Subject')['Mean'].idxmax()]

    fig = px.bar(
        top_methods,
        x='Subject',
        y='Mean',
        color='TeachingMethod',
        title='Top Performing Teaching Method per Subject',
        template='plotly_dark',
        color_discrete_map=teaching_method_colors
    )

    st.plotly_chart(fig, use_container_width=True)


# Tab 3 - Overall Method Comparison
with tab3:
    st.header("Overall Average Score by Teaching Method")
    overall_means = df_melted.groupby('TeachingMethod')['Score'].mean().reset_index()

    fig = px.bar(
        overall_means,
        x='TeachingMethod',
        y='Score',
        title='Overall Average Score by Teaching Method',
        template='plotly_dark',
        color='TeachingMethod',
        color_discrete_map=teaching_method_colors
    )

    st.plotly_chart(fig, use_container_width=True)


# Tab 4 - Mean Scores Comparison
with tab4:
    st.header("Mean Scores by Subject and Method")
    fig = px.bar(
        descriptive_stats,
        x='Subject',
        y='Mean',
        color='TeachingMethod',
        barmode='group',
        title='Mean Score Comparison by Subject and Method',
        template='plotly_dark',
        color_discrete_map=teaching_method_colors
    )
    st.plotly_chart(fig, use_container_width=True)


# Tab 5 - Summary and P-value Visual
with tab5:
    st.header("Statistical Summary and Interpretation")

    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader("Key Finding")
        st.success("Teaching methods have a statistically significant impact on student performance.")
        st.markdown("**P-value = 2.2e-16**")

    with col2:
        st.subheader("P-Value Decision Zone")
        pval_fig = go.Figure()
        pval_fig.add_shape(type='rect', x0=0.05, x1=1, y0=0, y1=1, fillcolor='lightgrey', line=dict(width=0))
        pval_fig.add_shape(type='rect', x0=0, x1=0.05, y0=0, y1=1, fillcolor='lightgreen', line=dict(width=0))
        pval_fig.add_trace(go.Scatter(
            x=[2.2e-16], y=[0.5],
            mode='markers+text',
            marker=dict(size=12, color='red'),
            text=["p = 2.2e-16"],
            textposition="bottom center"
        ))
        pval_fig.update_layout(
            xaxis_title="P-value",
            yaxis=dict(visible=False),
            xaxis=dict(range=[0, 0.1]),
            height=200,
            template="plotly_white",
            showlegend=False
        )
        st.plotly_char