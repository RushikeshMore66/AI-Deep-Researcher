import streamlit as st
import time
from core.orchestrator import ResearchOrchestrator
from modules.report_generator import render_markdown
from config.settings import settings

# --- UI Configuration ---
st.set_page_config(
    page_title="Deep Researcher AI",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Premium Styling ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background: radial-gradient(circle at top right, #1a1a2e, #16213e);
        color: #e9ecef;
    }
    
    /* Header styling */
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(90deg, #00d2ff 0%, #3a7bd5 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    .sub-header {
        font-size: 1.2rem;
        color: #8892b0;
        margin-bottom: 2rem;
    }
    
    /* Card-like containers for glassmorphism */
    div.stButton > button:first-child {
        background: linear-gradient(90deg, #00d2ff 0%, #3a7bd5 100%);
        color: white;
        border: none;
        padding: 0.6rem 2rem;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    div.stButton > button:first-child:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(0, 210, 255, 0.4);
    }
    
    .report-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 2rem;
        border-radius: 12px;
        margin-top: 2rem;
    }
    
    /* Sidebar adjustments */
    .css-1d391kg {
        background-color: rgba(0, 0, 0, 0.2);
    }
    </style>
""", unsafe_allow_html=True)

# --- Sidebar Content ---
with st.sidebar:
    st.image("https://img.icons8.com/fluent/96/000000/brain.png", width=80)
    st.markdown("### Deep Researcher v2.0")
    st.markdown("---")
    st.info("The premier AI orchestration engine for deep corporate and market research.")
    
    st.markdown("#### Quick Queries")
    sample_queries = ["Tesla", "SpaceX", "Microsoft", "Future of Green Hydrogen"]
    for q in sample_queries:
        if st.button(q, key=f"btn_{q}"):
            st.session_state.search_query = q
    
    st.markdown("---")
    st.caption("Engineered for accuracy and professional depth.")

# --- Main Interface ---
st.markdown('<h1 class="main-header">Deep Researcher AI</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Intelligent multi-stage research orchestration for complex market analysis.</p>', unsafe_allow_html=True)

# Query Input
query = st.text_input("Enter company name or research topic", 
                     value=st.session_state.get("search_query", ""),
                     placeholder="e.g. NVIDIA or Carbon Capture Technology")

if st.button("Initialize Deep Research") or st.session_state.get("trigger_search"):
    if not query:
        st.warning("Please enter a research query.")
    else:
        # Prepare Progress UI
        progress_container = st.container()
        with progress_container:
            st.markdown("### ⚙️ Orchestration in Progress")
            progress_bar = st.progress(0)
            status_text = st.empty()
            log_container = st.expander("Pipeline Execution Logs", expanded=False)
            
            def update_progress(percent, message):
                progress_bar.progress(percent if percent >= 0 else 0)
                status_text.markdown(f"**Current Stage:** {message}")
                with log_container:
                    st.caption(f"[{time.strftime('%H:%M:%S')}] {message}")

        # Run Orchestrator
        try:
            start_time = time.time()
            orchestrator = ResearchOrchestrator(query, progress_callback=update_progress)
            report = orchestrator.run()
            duration = time.time() - start_time
            
            # --- Results Display ---
            st.success(f"Research compiled successfully in {duration:.2f} seconds.")
            
            tab1, tab2, tab3, tab4 = st.tabs(["📄 Executive Summary", "🔍 Analysis Sections", "⛓️ Evidence", "📊 Performance"])
            
            with tab1:
                st.markdown(f"### Executive Summary\n{report.executive_summary}")
                st.markdown("---")
                st.markdown("#### Strategic Watchlist")
                for item in report.what_to_watch_next:
                    st.markdown(f"- {item}")

            with tab2:
                for section in report.sections:
                    with st.expander(f"Analysis: {section.angle_title}", expanded=True):
                        if not section.findings:
                            st.write("Limited evidence-based findings for this specific angle.")
                        for finding in section.findings:
                            st.markdown(f"- {finding}")
            
            with tab3:
                if not report.evidence_bullets:
                    st.info("No explicit citations were mapped to findings.")
                else:
                    for bullet in report.evidence_bullets:
                        st.markdown(f"**Claim:** {bullet.claim}")
                        st.caption(f"Source: [{bullet.source_title}]({bullet.url})")
                        st.markdown("---")

            with tab4:
                col1, col2, col3 = st.columns(3)
                col1.metric("Citation Coverage", f"{report.quality_checks.citation_coverage*100:.0f}%")
                col2.metric("Source Diversity", report.quality_checks.source_diversity)
                col3.metric("Status", "Passed" if report.quality_checks.passed else "Incomplete")
                
                if not report.quality_checks.passed:
                    st.warning("Quality thresholds were not fully met. Key gaps identified:")
                    for gap in report.quality_checks.failed_checks:
                        st.markdown(f"- {gap}")
                
                if report.quality_checks.freshness_warnings:
                    st.info("Freshness Warnings:")
                    for w in report.quality_checks.freshness_warnings:
                        st.markdown(f"- {w}")

            # Option to see full Markdown
            with st.expander("View Full Markdown Raw"):
                st.code(render_markdown(report), language="markdown")

        except Exception as e:
            st.error(f"An error occurred during research: {e}")

# Clear trigger
if "trigger_search" in st.session_state:
    del st.session_state.trigger_search
