import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# -------------------- CONFIG & STYLE --------------------
st.set_page_config(layout="wide", page_title="Teaching Methods Dashboard")

# Sidebar style selector
st.sidebar.header("\U0001F3A8 Chart Style Options")
template_choice = st.sidebar.selectbox(
    "Choose a Plotly Template:",
    options=["ggplot2", "simple_white", "seaborn"],
    index=0
)

# Updated, balanced colors
subject_colors = {
    'EnglishScore': '#7DAEA3',   # eucalyptus teal
    'MathScore': '#A45D5D',      # warm clay red
    'ChemistryScore': '#F2C57C', # muted goldenrod
    'PhysicsScore': '#A18FC6',   # soft violet
    'BiologyScore': '#76B39D'    # updated botanical green
}

teaching_method_colors = {
    'Lecture-Based Instruction': '#9C9C9C',     # graphite
    'Facilitator': '#6BA6A8',                  # misty turquoise
    'Technology Based Learning': '#6488EA',    # updated azure blue
    'Group Learning': '#B6C867',               # sage lime
    'Individual Learning': '#D9D4CF',          # paper beige
    'Inquiry-Based Learning': '#7FB0C0',       # muted cyan
    'Differentiated Instruction': '#A989A0'    # dusty rose-mauve
}

# -------------------- DATA LOADING & CLEANING --------------------
df = pd.read_excel("teaching_data.xlsx", sheet_name='Sheet1')

df_melted = df.melt(id_vars=['StudentID', 'TeachingMethod'],
                    value_vars=['EnglishScore', 'MathScore', 'ChemistryScore', 'PhysicsScore', 'BiologyScore'],
                    var_name='Subject', value_name='Score')
df_melted['Subject'] = df_melted['Subject'].str.replace('Score', '')

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
st.markdown("# \U0001F393 *Teaching Method Effectiveness Dashboard*")
st.markdown("#### *An ESM 250 Final Project on Evidence-Based Pedagogy*")
st.markdown("##### _Where educational theory meets statistical insight_")
st.markdown("---")

# -------------------- TABS --------------------
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "\U0001F3AF CI Plots", "\U0001F3C6 Top Methods", "\U0001F4C8 Overall Comparison",
    "\U0001F4DA Subject Breakdown", "\U0001F4CA MANOVA & Stats", "\U0001F4CB Raw Summary Table"
])

# -------------------- TAB 1 --------------------
with tab1:
    st.markdown("### \U0001F3AF Confidence Intervals: Mean Scores by Method")
    st.caption("Each bar shows the average student score for a given subject and teaching method, including a 95% confidence interval.")
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
            template=template_choice,
            margin=dict(t=60, b=40, l=60, r=40)
        )
        st.plotly_chart(fig, use_container_width=True)

# -------------------- TAB 2 --------------------
with tab2:
    st.markdown("### \U0001F3C6 Top Performing Teaching Methods")
    st.caption("For each subject, the teaching method that yielded the highest average score is shown.")
    top_methods = descriptive_stats.loc[descriptive_stats.groupby('Subject')['Mean'].idxmax()]
    fig = px.bar(top_methods, x='Subject', y='Mean', color='TeachingMethod',
                 title='Best Method by Subject', template=template_choice,
                 color_discrete_map=teaching_method_colors)
    st.plotly_chart(fig, use_container_width=True)

# -------------------- TAB 3 --------------------
with tab3:
    st.markdown("### \U0001F4C8 Overall Teaching Method Comparison")
    st.caption("Average of all subject scores per method.")
    overall_means = df_melted.groupby('TeachingMethod')['Score'].mean().reset_index()
    fig = px.bar(overall_means, x='TeachingMethod', y='Score',
                 title='Average Score by Teaching Method',
                 template=template_choice, color='TeachingMethod',
                 color_discrete_map=teaching_method_colors)
    st.plotly_chart(fig, use_container_width=True)

# -------------------- TAB 4 --------------------
with tab4:
    st.markdown("### \U0001F4DA Score Breakdown by Subject and Method")
    st.caption("Grouped bar chart showing how each teaching method performed across subjects.")
    fig = px.bar(descriptive_stats, x='Subject', y='Mean', color='TeachingMethod',
                 barmode='group', title='Method Comparison per Subject',
                 template=template_choice, color_discrete_map=teaching_method_colors)
    st.plotly_chart(fig, use_container_width=True)

# -------------------- TAB 5 --------------------
with tab5:
    st.markdown("### \U0001F4CA MANOVA Results & Statistical Summary")
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
    **\U0001F3DB️ Interpretation:**
    - The extremely low p-value indicates **strong statistical evidence** that teaching methods influence student outcomes.
    - **Different methods yield measurably different performance**.

    **MANOVA Framework**
    - **H₀**: Teaching styles have no effect on performance.
    - **H₁**: At least one style significantly differs.
    - **Conclusion**: Reject H₀. Teaching method matters.
    """)

# -------------------- TAB 6 --------------------
with tab6:
    st.markdown("### \U0001F4CB Full Descriptive Statistics Table")
    st.caption("Includes mean, median, standard deviation, confidence interval, and more.")
    st.dataframe(descriptive_stats.round(2), use_container_width=True)
