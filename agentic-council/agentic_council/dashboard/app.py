"""Streamlit dashboard for Agentic Council."""

import asyncio
import json
from datetime import datetime

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# Page config
st.set_page_config(
    page_title="Agentic Council",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown("""
<style>
    .stProgress > div > div > div > div {
        background-color: #1f77b4;
    }
    .vote-card {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 0.5rem;
    }
    .vote-go { background-color: #d4edda; border-left: 4px solid #28a745; }
    .vote-no-go { background-color: #f8d7da; border-left: 4px solid #dc3545; }
    .vote-conditional { background-color: #fff3cd; border-left: 4px solid #ffc107; }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialize session state variables."""
    if "council" not in st.session_state:
        st.session_state.council = None
    if "current_session" not in st.session_state:
        st.session_state.current_session = None
    if "evaluation_running" not in st.session_state:
        st.session_state.evaluation_running = False
    if "history" not in st.session_state:
        st.session_state.history = []


def render_sidebar():
    """Render sidebar with configuration options."""
    st.sidebar.title("Council Configuration")

    st.sidebar.subheader("Time Limits")
    total_time = st.sidebar.slider("Total Time (seconds)", 300, 1800, 900)
    phase1_time = st.sidebar.slider("Phase 1 (seconds)", 60, 600, 300)
    phase2_time = st.sidebar.slider("Phase 2 (seconds)", 120, 900, 420)
    phase3_time = st.sidebar.slider("Phase 3 (seconds)", 60, 300, 180)

    st.sidebar.subheader("Risk Appetite")
    risk_appetite = st.sidebar.select_slider(
        "Risk Tolerance",
        options=["Conservative", "Moderate", "Aggressive"],
        value="Moderate"
    )

    st.sidebar.subheader("Agents")
    enable_da = st.sidebar.checkbox("Enable Devil's Advocate", value=True)

    return {
        "total_time": total_time,
        "phase1_time": phase1_time,
        "phase2_time": phase2_time,
        "phase3_time": phase3_time,
        "risk_appetite": risk_appetite.lower(),
        "enable_devils_advocate": enable_da,
    }


def render_idea_input():
    """Render the idea input section."""
    st.header("Evaluate Your Business Idea")

    idea = st.text_area(
        "Describe your business idea",
        height=150,
        placeholder="Enter a detailed description of your business idea...",
        help="Provide as much detail as possible for better evaluation"
    )

    col1, col2 = st.columns(2)

    with col1:
        industry = st.selectbox(
            "Industry",
            ["Technology", "Healthcare", "Finance", "E-commerce", "Education", "Entertainment", "Other"]
        )

    with col2:
        funding_stage = st.selectbox(
            "Funding Stage",
            ["Pre-seed", "Seed", "Series A", "Series B+", "Bootstrapped"]
        )

    additional_context = st.text_area(
        "Additional Context (optional)",
        height=100,
        placeholder="Market research, competitor analysis, team background..."
    )

    return {
        "idea": idea,
        "context": {
            "industry": industry,
            "funding_stage": funding_stage,
            "additional_info": additional_context,
        }
    }


def render_live_debate(session_data):
    """Render live debate view."""
    st.header("Council Deliberation")

    # Time progress
    if session_data.get("time_status"):
        time_status = session_data["time_status"]
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Phase", time_status.get("current_phase", "N/A"))
        with col2:
            st.metric("Time Remaining", f"{time_status.get('total_remaining', 0):.0f}s")
        with col3:
            progress = 1 - (time_status.get("total_remaining", 900) / 900)
            st.progress(progress)

    # Agent positions
    st.subheader("Agent Positions")

    positions = session_data.get("positions", {})
    if positions:
        cols = st.columns(3)
        for idx, (agent, pos) in enumerate(positions.items()):
            with cols[idx % 3]:
                vote_class = "vote-go" if pos.get("score", 5) >= 6 else \
                            "vote-no-go" if pos.get("score", 5) <= 4 else "vote-conditional"

                st.markdown(f"""
                <div class="vote-card {vote_class}">
                    <strong>{agent}</strong><br>
                    Score: {pos.get('score', 'N/A')}/10<br>
                    Vote: {pos.get('vote', 'N/A')}<br>
                    Confidence: {pos.get('confidence', 0):.0%}
                </div>
                """, unsafe_allow_html=True)

    # Debate transcript
    st.subheader("Debate Transcript")

    transcript = session_data.get("transcript", [])
    for entry in transcript[-10:]:  # Last 10 entries
        if entry.get("type") == "agent_response":
            with st.expander(f"{entry.get('agent', 'Agent')} - {entry.get('role', '')}", expanded=False):
                st.write(entry.get("content", ""))
        elif entry.get("type") == "phase_start":
            st.info(f"Starting Phase: {entry.get('phase', '')}")
        elif entry.get("type") == "vote":
            st.success(f"{entry.get('agent', '')} voted: {entry.get('vote', '')} (Score: {entry.get('score', '')})")


def render_results(session):
    """Render evaluation results."""
    st.header("Evaluation Results")

    if not session or not session.final_consensus:
        st.warning("No results available")
        return

    consensus = session.final_consensus

    # Main recommendation
    rec_color = {
        "strong_go": "#28a745",
        "go": "#20c997",
        "conditional_go": "#ffc107",
        "no_go": "#fd7e14",
        "strong_no_go": "#dc3545",
    }.get(consensus.recommendation.value, "#6c757d")

    st.markdown(f"""
    <div style="background-color: {rec_color}; color: white; padding: 2rem;
                border-radius: 1rem; text-align: center; margin-bottom: 1rem;">
        <h1>{consensus.recommendation.value.upper().replace('_', ' ')}</h1>
        <h3>Confidence: {consensus.confidence:.0%}</h3>
    </div>
    """, unsafe_allow_html=True)

    # Key metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Weighted Score", f"{consensus.weighted_score:.1f}/10")
    with col2:
        st.metric("GO Votes", consensus.aggregation.go_votes)
    with col3:
        st.metric("NO-GO Votes", consensus.aggregation.no_go_votes)
    with col4:
        st.metric("Consensus Level", f"{consensus.aggregation.consensus_level:.0%}")

    # Key drivers and risks
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Key Drivers")
        for driver in consensus.key_drivers:
            st.markdown(f"+ {driver}")

    with col2:
        st.subheader("Major Risks")
        for risk in consensus.major_risks:
            st.markdown(f"- {risk}")

    # Risk assessment
    st.subheader("Risk Assessment")
    st.text(consensus.risk_assessment)

    # Dissenting opinions
    if consensus.dissenting_opinions:
        st.subheader("Dissenting Opinions")
        for dissent in consensus.dissenting_opinions:
            with st.expander(f"{dissent.agent_name} - {dissent.vote.value}"):
                st.write(dissent.reasoning)


def render_vote_chart(session):
    """Render vote visualization chart."""
    if not session or not session.phase_results:
        return

    # Get final votes
    votes = []
    for pr in session.phase_results:
        if pr.phase_name == "consensus_building":
            for vote in pr.votes:
                votes.append({
                    "Agent": vote.agent_name,
                    "Score": vote.score,
                    "Confidence": vote.confidence,
                    "Vote": vote.vote.value,
                })

    if not votes:
        return

    df = pd.DataFrame(votes)

    # Score bar chart
    fig = px.bar(
        df,
        x="Agent",
        y="Score",
        color="Vote",
        color_discrete_map={
            "strong_go": "#28a745",
            "go": "#20c997",
            "conditional_go": "#ffc107",
            "no_go": "#fd7e14",
            "strong_no_go": "#dc3545",
        },
        title="Agent Scores",
    )
    fig.update_layout(yaxis_range=[0, 10])
    st.plotly_chart(fig, use_container_width=True)

    # Radar chart for confidence
    fig2 = go.Figure()
    fig2.add_trace(go.Scatterpolar(
        r=df["Confidence"].tolist(),
        theta=df["Agent"].tolist(),
        fill="toself",
        name="Confidence"
    ))
    fig2.update_layout(
        polar=dict(radialaxis=dict(range=[0, 1])),
        title="Agent Confidence Levels"
    )
    st.plotly_chart(fig2, use_container_width=True)


def render_phase_timeline(session):
    """Render phase timeline visualization."""
    if not session or not session.phase_results:
        return

    phases = []
    cumulative_time = 0

    for pr in session.phase_results:
        phases.append({
            "Phase": pr.phase_name.replace("_", " ").title(),
            "Start": cumulative_time,
            "Duration": pr.duration_seconds,
            "Responses": len(pr.agent_responses),
        })
        cumulative_time += pr.duration_seconds

    df = pd.DataFrame(phases)

    fig = px.timeline(
        df,
        x_start="Start",
        x_end=df["Start"] + df["Duration"],
        y="Phase",
        color="Phase",
        title="Phase Timeline",
    )
    st.plotly_chart(fig, use_container_width=True)


def render_backtest_results(results):
    """Render backtest results."""
    st.header("Historical Backtest Results")

    if not results:
        st.warning("No backtest results available")
        return

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)

    stats = {
        "total": len(results),
        "passed": sum(1 for r in results if r.passed),
        "avg_accuracy": sum(r.accuracy.overall_accuracy for r in results) / len(results),
    }

    with col1:
        st.metric("Total Tests", stats["total"])
    with col2:
        st.metric("Passed", stats["passed"])
    with col3:
        st.metric("Failed", stats["total"] - stats["passed"])
    with col4:
        st.metric("Avg Accuracy", f"{stats['avg_accuracy']:.0%}")

    # Results table
    data = []
    for r in results:
        data.append({
            "Test": r.test_case.id,
            "Year": r.test_case.year,
            "Actual": "SUCCESS" if r.test_case.actual_outcome.success else "FAILURE",
            "Predicted": r.session.final_consensus.recommendation.value.upper()
            if r.session.final_consensus else "N/A",
            "Passed": "Yes" if r.passed else "No",
            "Accuracy": f"{r.accuracy.overall_accuracy:.0%}",
        })

    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True)

    # Accuracy breakdown chart
    dimension_data = []
    for r in results:
        dimension_data.append({
            "Test": r.test_case.id,
            "Direction": r.accuracy.dimension_scores.direction,
            "Risk Precision": r.accuracy.dimension_scores.risk_precision,
            "Driver Accuracy": r.accuracy.dimension_scores.driver_accuracy,
            "Timing": r.accuracy.dimension_scores.timing,
        })

    df_dims = pd.DataFrame(dimension_data)
    fig = px.bar(
        df_dims.melt(id_vars=["Test"], var_name="Dimension", value_name="Score"),
        x="Test",
        y="Score",
        color="Dimension",
        barmode="group",
        title="Accuracy by Dimension",
    )
    fig.update_layout(yaxis_range=[0, 1])
    st.plotly_chart(fig, use_container_width=True)


def main():
    """Main dashboard entry point."""
    init_session_state()

    st.title("Agentic Council Dashboard")
    st.markdown("*Multi-agent business idea evaluation system*")

    # Sidebar configuration
    config = render_sidebar()

    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "Evaluate",
        "Live Debate",
        "Results",
        "Backtest"
    ])

    with tab1:
        inputs = render_idea_input()

        if st.button("Start Evaluation", type="primary", disabled=st.session_state.evaluation_running):
            if not inputs["idea"]:
                st.error("Please enter a business idea")
            else:
                st.session_state.evaluation_running = True
                st.info("Evaluation started... This may take 1-3 minutes.")

                # Note: In production, this would call the actual council
                # For demo, we show a placeholder
                st.warning("Connect to API server to run actual evaluation")

    with tab2:
        st.subheader("Live Debate View")

        if st.session_state.current_session:
            render_live_debate({
                "time_status": {"current_phase": "structured_debate", "total_remaining": 450},
                "positions": {},
                "transcript": [],
            })
        else:
            st.info("Start an evaluation to see the live debate")

    with tab3:
        if st.session_state.current_session:
            render_results(st.session_state.current_session)

            st.subheader("Visualizations")
            col1, col2 = st.columns(2)

            with col1:
                render_vote_chart(st.session_state.current_session)

            with col2:
                render_phase_timeline(st.session_state.current_session)
        else:
            st.info("Complete an evaluation to see results")

    with tab4:
        st.subheader("Historical Backtesting")

        if st.button("Run All Backtests"):
            st.warning("Connect to API server to run backtests")

        # Demo results
        st.info("Backtest results will appear here after running tests")


if __name__ == "__main__":
    main()
