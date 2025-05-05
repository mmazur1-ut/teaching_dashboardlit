import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# -------------------- CONFIG & ACADEMIA + NATURE AESTHETICS --------------------
st.set_page_config(layout="wide", page_title="Teaching Methods Dashboard")

subject_colors = {
    'EnglishScore': '#A3C4BC',   # eucalyptus sage
    'MathScore': '#6B9080',      # pine green
    'ChemistryScore': '#CCE3DC', # seafoam mist
    'PhysicsScore': '#D5C6E0',   # lilac fog
    'BiologyScore': '#A4C3B2'    # leafy green
}

teaching_method_colors = {
    'Lecture-Based Instruction': '#7E8D85',     # mossy grey
    'Facilitator': '#C1DADB',                  # blue mist
    'Technology Based Learning': '#87BBA2',    # modern forest green
    'Group Learning': '#BFD8B8',               # soft fern
    'Individual Learning': '#E4EFE7',          # off-white mint
    'Inquiry-Based Learning': '#96C9DC',       # glacial blue
    'Differentiated Instruction': '#A69CAC'    # soft mauve
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
st.markdown("# 🎓 *Teaching Method Effectiveness Dashboard*")
st.markdown("#### *An ESM 250 Final Project on Evidence-Based Pedagogy*")
st.markdown("##### _Where educational theory meets statistical insight_")
st.markdown("---")

# -------------------- TABS --------------------
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🎯 CI Plots", "🥇 Top Methods", "📈 Overall Comparison",
    "📚 Subject Breakdown", "📊 MANOVA & Stats", "📋 Raw Summary Table"
])

# -------------------- TAB 1 --------------------
with tab1:
    st.markdown("### 🎯 Confidence Intervals: Mean Scores by Method")
    st.caption("Each bar shows the average student score for a given subject and teaching method, including a 95% confidence interval. This visual helps evaluate the precision of the estimates across approaches.")
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
            title=f"{subject} – Mean Score with 95% CI",
            xaxis_title="Teaching Method",
            yaxis_title="Mean Score",
            template="plotly_dark",
            margin=dict(t=60, b=40, l=60, r=40)
        )
        st.plotly_chart(fig, use_container_width=True)

# -------------------- TAB 2 --------------------
with tab2:
    st.markdown("### 🥇 Top Performing Teaching Methods")
    st.caption("For each subject, the teaching method that yielded the highest average score is shown. This offers a subject-specific view into which instructional style works best.")
    top_methods = descriptive_stats.loc[descriptive_stats.groupby('Subject')['Mean'].idxmax()]
    fig = px.bar(top_methods, x='Subject', y='Mean', color='TeachingMethod',
                 title='Best Method by Subject', template='plotly_dark',
                 color_discrete_map=teaching_method_colors)
    st.plotly_chart(fig, use_container_width=True)

# -------------------- TAB 3 --------------------
with tab3:
    st.markdown("### 📈 Overall Teaching Method Comparison")
    st.caption("This chart averages student scores across all subjects for each method — giving a high-level perspective on overall performance.")
    overall_means = df_melted.groupby('TeachingMethod')['Score'].mean().reset_index()
    fig = px.bar(overall_means, x='TeachingMethod', y='Score',
                 title='Average Score by Teaching Method',
                 template='plotly_dark', color='TeachingMethod',
                 color_discrete_map=teaching_method_colors)
    st.plotly_chart(fig, use_container_width=True)

# -------------------- TAB 4 --------------------
with tab4:
    st.markdown("### 📚 Score Breakdown by Subject and Method")
    st.caption("A grouped bar chart showing how each teaching method performed across different subjects. Useful for comparing instructional style performance side by side.")
    fig = px.bar(descriptive_stats, x='Subject', y='Mean', color='TeachingMethod',
                 barmode='group', title='Method Comparison per Subject',
                 template='plotly_dark', color_discrete_map=teaching_method_colors)
    st.plotly_chart(fig, use_container_width=True)

# -------------------- TAB 5 --------------------
with tab5:
    st.markdown("### 📊 MANOVA Results & Statistical Summary")
    col1, col2 = st.columns([1, 1])
    with col1:
        st.success("The MANOVA test reveals a statistically significant effect of teaching method on student scores.")
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
    **🏛️ Interpretation:**
    - The extremely low p-value indicates **strong statistical evidence** that teaching methods influence student outcomes.
    - **Different methods yield measurably different performance**.
    - These results can support curriculum decisions or teaching training models.

    **MANOVA Framework**
    - **H₀**: Teaching styles have no effect on performance.
    - **H₁**: At least one style significantly differs.
    - **Conclusion**: Reject H₀. Teaching method matters.
    """)

# -------------------- TAB 6 --------------------
with tab6:
    st.markdown("### 📋 Full Descriptive Statistics Table")
    st.caption("A raw table of statistical summaries including mean, median, standard deviation, and more — organized by subject and method.")
    st.dataframe(descriptive_stats.round(2), use_container_width=True)
