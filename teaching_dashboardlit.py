import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# -------------------- CONFIG & COLOR THEMES --------------------
st.set_page_config(layout="wide", page_title="Teaching Methods Dashboard")

subject_colors = {
    'EnglishScore': '#8FB9A8',  # Sage green
    'MathScore': '#4D77FF',     # Soft blue
    'ChemistryScore': '#6AD1E3',
    'PhysicsScore': '#be90cf',
    'BiologyScore': '#64d488'
}

teaching_method_colors = {
    'Lecture-Based Instruction': '#5B6C8F',
    'Facilitator': '#84DCC6',
    'Technology Based Learning': '#3B8EA5',
    'Group Learning': '#88c081',
    'Individual Learning': '#A6E3E9',
    'Inquiry-Based Learning': '#68A691',
    'Differentiated Instruction': '#D76A8A'
}

# -------------------- DATA LOADING & CLEANING --------------------
df = pd.read_excel("teaching_data.xlsx", sheet_name='Sheet1')

df_melted = df.melt(id_vars=['StudentID', 'TeachingMethod'],
                    value_vars=['EnglishScore', 'MathScore', 'ChemistryScore', 'PhysicsScore', 'BiologyScore'],
                    var_name='Subject', value_name='Score')
df_melted['Subject'] = df_melted['Subject'].str.replace('Score', '')  # Clean names

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

descriptive_stats['CI'] = 1.96 * (descriptive_stats['StdDev'] / np.sqrt(descriptive_stats['Count']))

# -------------------- UI HEADER --------------------
st.markdown("# 🧑‍🏫 Teaching Method Effectiveness Dashboard")
st.markdown("#### *ESM 250 – Final Project*")
st.markdown("---")

# -------------------- TABS --------------------
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🎯 Mean ± 95% CI", "🥇 Top Methods", "📈 Overall Comparison",
    "📚 Subject vs. Method", "📊 Summary & Stats", "📋 Full Table"
])

# -------------------- TAB 1 --------------------
with tab1:
    st.markdown("### 🎯 Mean Scores ± 95% Confidence Intervals")
    st.caption("Each bar shows the average score for students under each teaching method, with error bars representing the 95% confidence interval. This helps estimate the reliability of the observed mean.")
    for subject in df_melted['Subject'].unique():
        sub_data = descriptive_stats[descriptive_stats['Subject'] == subject]
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=sub_data['TeachingMethod'],
            y=sub_data['Mean'],
            error_y=dict(type='data', array=sub_data['CI'], visible=True),
            name=subject,
            marker_color=subject_colors.get(subject + 'Score', '#CCCCCC')
        ))
        fig.update_layout(
            title=f"{subject} – Mean Score with 95% Confidence Interval",
            xaxis_title="Teaching Method",
            yaxis_title="Mean Score",
            template="plotly_dark",
            margin=dict(t=60, b=40, l=60, r=40)
        )
        st.plotly_chart(fig, use_container_width=True)

# -------------------- TAB 2 --------------------
with tab2:
    st.markdown("### 🥇 Top Performing Methods by Subject")
    st.caption("This highlights the highest-scoring teaching method for each subject. Use it to quickly identify subject-specific strengths across teaching styles.")
    top_methods = descriptive_stats.loc[descriptive_stats.groupby('Subject')['Mean'].idxmax()]
    fig = px.bar(top_methods, x='Subject', y='Mean', color='TeachingMethod',
                 title='Top Performing Teaching Method per Subject',
                 template='plotly_dark', color_discrete_map=teaching_method_colors)
    st.plotly_chart(fig, use_container_width=True)

# -------------------- TAB 3 --------------------
with tab3:
    st.markdown("### 📈 Overall Average Score by Method")
    st.caption("Here we average scores across all subjects for each method. It offers a big-picture view of which strategies generally yield the best results.")
    overall_means = df_melted.groupby('TeachingMethod')['Score'].mean().reset_index()
    fig = px.bar(overall_means, x='TeachingMethod', y='Score',
                 title='Overall Average Score by Teaching Method',
                 template='plotly_dark', color='TeachingMethod',
                 color_discrete_map=teaching_method_colors)
    st.plotly_chart(fig, use_container_width=True)

# -------------------- TAB 4 --------------------
with tab4:
    st.markdown("### 📚 Mean Scores by Subject and Method")
    st.caption("This grouped bar chart lets you compare how different teaching methods performed across all subjects side by side.")
    fig = px.bar(descriptive_stats, x='Subject', y='Mean', color='TeachingMethod',
                 barmode='group', title='Mean Score Comparison by Subject and Method',
                 template='plotly_dark', color_discrete_map=teaching_method_colors)
    st.plotly_chart(fig, use_container_width=True)

# -------------------- TAB 5 --------------------
with tab5:
    st.markdown("### 📊 Statistical Summary and Interpretation")
    col1, col2 = st.columns([1, 1])
    with col1:
        st.success("Teaching methods have a statistically significant impact on student performance.")
        st.markdown("**P-value = 2.2e-16**")
    with col2:
        pval_fig = go.Figure()
        pval_fig.add_shape(type='rect', x0=0.05, x1=1, y0=0, y1=1, fillcolor='lightgrey', line=dict(width=0))
        pval_fig.add_shape(type='rect', x0=0, x1=0.05, y0=0, y1=1, fillcolor='lightgreen', line=dict(width=0))
        pval_fig.add_trace(go.Scatter(
            x=[2.2e-16], y=[0.5], mode='markers+text',
            marker=dict(size=12, color='red'),
            text=["p = 2.2e-16"], textposition="bottom center"
        ))
        pval_fig.update_layout(
            xaxis_title="P-value", yaxis=dict(visible=False),
            xaxis=dict(range=[0, 0.1]), height=200,
            template="plotly_white", showlegend=False
        )
        st.plotly_chart(pval_fig, use_container_width=True)
    st.markdown("---")
    st.markdown("""
    **📌 How to Interpret This:**
    - A p-value this small means there is **strong evidence** that not all teaching styles are equally effective.
    - **Some methods consistently lead to better student scores**.
    - This can inform policy or instructional design decisions.

    **MANOVA Summary**
    - **H₀**: All teaching styles produce the same outcomes.
    - **H₁**: At least one teaching style is significantly different.
    - **Result**: P = 2.2e-16 → **Reject H₀**. Teaching styles differ significantly.
    """)

# -------------------- TAB 6 --------------------
with tab6:
    st.markdown("### 📋 Full Descriptive Statistics Table")
    st.caption("A full breakdown of central tendency and variability for each subject-method combo. Useful for deeper statistical insight or custom comparisons.")
    st.dataframe(descriptive_stats.round(2), use_container_width=True)
