import streamlit as st
import asyncio
import os
from dotenv import load_dotenv
from typing import List, Dict, Any
from agents import Runner, trace, gen_trace_id
from workers import planner_agent, web_search_agent, video_search_agent, writer_agent
from models.schemas import WebSearchItem

# Initialize environment
load_dotenv(override=True)

# Set page title and configuration
st.set_page_config(
    page_title="AI Deep Research Assistant",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Helper functions
async def plan_searches(query: str):
    """Use the planner_agent to plan which searches to run for the query"""
    with st.status("Planning search strategy...", expanded=True) as status:
        result = await Runner.run(planner_agent, f"query: {query}")

        # Sort searches by priority (highest first)
        sorted_searches = sorted(
            result.final_output.searches,
            key=lambda s: s.priority if hasattr(s, 'priority') else 5,
            reverse=True
        )

        web_searches = [s for s in sorted_searches if s.search_type == 'web']
        video_searches = [s for s in sorted_searches if s.search_type == 'video']

        status.update(label="Search strategy complete!", state="complete", expanded=False)

        # Return for display in UI
        return sorted_searches, web_searches, video_searches, result.final_output.strategy


async def perform_web_search(item: WebSearchItem):
    """Use the web search agent to run a web search"""
    priority = getattr(item, 'priority', 5)

    input_text = f"search query: {item.query}\nreason for searching: {item.reason}"
    result = await Runner.run(web_search_agent, input_text)

    return {
        "type": "web",
        "query": item.query,
        "reason": item.reason,
        "priority": priority,
        "result": result.final_output
    }


async def perform_video_search(item: WebSearchItem):
    """Use the video search agent to run a video search"""
    priority = getattr(item, 'priority', 6)

    input_text = f"search query: {item.query}\nreason for searching: {item.reason}"
    result = await Runner.run(video_search_agent, input_text)

    return {
        "type": "video",
        "query": item.query,
        "reason": item.reason,
        "priority": priority,
        "result": result.final_output
    }


async def perform_searches(searches: List[WebSearchItem]):
    """Execute all planned searches in parallel for better performance"""
    with st.status("Executing all searches in parallel...", expanded=True) as status:
        st.write(f"Running {len(searches)} searches simultaneously...")

        # Define a helper function to determine which search to perform
        async def search(item):
            if item.search_type == 'web':
                return await perform_web_search(item)
            elif item.search_type == 'video':
                return await perform_video_search(item)

        # Create tasks for all searches to run in parallel
        tasks = [asyncio.create_task(search(item)) for item in searches]

        # Execute all searches concurrently and wait for all to complete
        results = await asyncio.gather(*tasks)

        # Update status once all searches are done
        status.update(label=f"All {len(searches)} searches completed successfully!", state="complete", expanded=False)

        return results


async def write_report(query: str, search_results: List[Dict[str, Any]]):
    """Use the writer agent to write a comprehensive deep research report"""
    with st.status("Creating comprehensive research report...", expanded=True) as status:
        # Extract and format the search results
        web_results = [r for r in search_results if r["type"] == "web"]
        video_results = [r for r in search_results if r["type"] == "video"]

        # Create a structured overview of sources and findings
        web_sources_summary = "\n\n## WEB SOURCES OVERVIEW:\n\n"
        web_sources_summary += "| Search Query | Key Topics Covered |\n"
        web_sources_summary += "|-------------|--------------------|\n"
        for res in web_results:
            topics = res["query"].replace("2023", "").strip()
            web_sources_summary += f"| {res['query']} | {topics} |\n"

        # Detailed web findings
        web_text = "\n\n## DETAILED WEB RESEARCH FINDINGS:\n\n"
        for i, res in enumerate(web_results, 1):
            web_text += f"### Source {i}: {res['query']}\n"
            web_text += f"**Research Objective**: {res['reason']}\n\n"
            web_text += f"**Findings**:\n{res['result']}\n\n"
            web_text += "-" * 50 + "\n\n"

        # Video resources
        video_text = "\n\n## VIDEO RESOURCES IDENTIFIED:\n\n"
        for i, res in enumerate(video_results, 1):
            video_text += f"### Video Source {i}: {res['query']}\n"
            video_text += f"**Selection Purpose**: {res['reason']}\n\n"
            video_text += f"**Available Content**:\n{res['result']}\n\n"
            video_text += "-" * 50 + "\n\n"

        # Creating a structured research brief for the writer agent
        input_text = f"""# COMPREHENSIVE RESEARCH ASSIGNMENT

## Primary Research Query:
{query}

## Research Scope:
This is a request for a COMPREHENSIVE research report that must cover:
1. Historical foundations and theoretical principles
2. Current state-of-the-art and recent developments
3. Technical details and mechanisms
4. Applications across different domains
5. Key players and their contributions
6. Challenges, limitations, and debates
7. Future directions and possibilities

{web_sources_summary}

{web_text}

{video_text}

## Report Requirements:
1. Create an authoritative, comprehensive report (2500-3000+ words)
2. Balance historical context with cutting-edge developments
3. Include both foundational concepts AND technical details
4. Cover the ENTIRE landscape of {query}
5. Follow all formatting requirements from your instructions
6. Use all available sources to create a definitive resource on this topic

Remember to synthesize findings across all sources into a cohesive narrative, not just summarize individual search results.
"""

        status.update(label="Synthesizing research findings...", state="running")
        result = await Runner.run(writer_agent, input_text)
        status.update(label="Research report complete!", state="complete", expanded=False)

        return result.final_output


def initialize_session_state():
    """Initialize session state variables if they don't exist"""
    if 'api_keys_set' not in st.session_state:
        st.session_state.api_keys_set = False
    if 'research_completed' not in st.session_state:
        st.session_state.research_completed = False
    if 'search_plan' not in st.session_state:
        st.session_state.search_plan = None
    if 'search_results' not in st.session_state:
        st.session_state.search_results = None
    if 'report' not in st.session_state:
        st.session_state.report = None


def check_api_keys():
    """Check if API keys are set in environment variables or session state"""
    openai_key = os.environ.get('OPENAI_API_KEY') or st.session_state.get('openai_api_key')
    serper_key = os.environ.get('SERPER_API_KEY') or st.session_state.get('serper_api_key')
    return openai_key and serper_key


def main():
    """Main Streamlit application"""
    st.title("🔍 Deep Research Assistant")
    st.subheader("AI-powered comprehensive research reports")

    # Initialize session state
    initialize_session_state()

    # Sidebar for API keys
    # In your app.py file, update the sidebar API key handling:

    with st.sidebar:
        st.header("API Configuration")

        # Check if API keys are already in environment variables
        openai_key_exists = bool(os.environ.get('OPENAI_API_KEY'))
        serper_key_exists = bool(os.environ.get('SERPER_API_KEY'))

        if openai_key_exists and serper_key_exists:
            st.success("✅ API keys found in environment variables")
            st.session_state.api_keys_set = True
        else:
            st.warning("⚠️ API keys are required to run this application")

            # Only show input fields if keys are not in environment variables
            openai_key = st.text_input(
                "OpenAI API Key" + (" (not set)" if not openai_key_exists else " (already set)"),
                type="password",
                value=os.environ.get('OPENAI_API_KEY', ''),
                help="Required for the AI agents to function",
                disabled=openai_key_exists
            )

            serper_key = st.text_input(
                "Serper API Key" + (" (not set)" if not serper_key_exists else " (already set)"),
                type="password",
                value=os.environ.get('SERPER_API_KEY', ''),
                help="Required for web and video searches",
                disabled=serper_key_exists
            )

            # Only show save button if at least one key is missing
            if not (openai_key_exists and serper_key_exists):
                if st.button("Save API Keys"):
                    # Update any keys that were entered
                    if not openai_key_exists and openai_key:
                        os.environ['OPENAI_API_KEY'] = openai_key
                        openai_key_exists = True

                    if not serper_key_exists and serper_key:
                        os.environ['SERPER_API_KEY'] = serper_key
                        serper_key_exists = True

                    # Update session state based on whether all required keys are now set
                    st.session_state.api_keys_set = openai_key_exists and serper_key_exists

                    if st.session_state.api_keys_set:
                        st.success("✅ All API keys saved successfully!")
                        st.experimental_rerun()  # Refresh to update the UI
                    else:
                        missing_keys = []
                        if not openai_key_exists:
                            missing_keys.append("OpenAI API Key")
                        if not serper_key_exists:
                            missing_keys.append("Serper API Key")
                        st.error(f"❌ Missing keys: {', '.join(missing_keys)}")

        st.markdown("---")

        # About section
        st.header("About")
        st.markdown("""
        This app uses a multi-agent system to perform deep research on any topic:

        1. **Planning Agent**: Designs a strategic research plan
        2. **Web Search Agent**: Gathers information from the web
        3. **Video Search Agent**: Identifies relevant video resources
        4. **Writer Agent**: Synthesizes findings into a comprehensive report
        """)

    # Main interface
    query = st.text_input("Enter your research topic:", placeholder="e.g., Latest AI Agent frameworks in 2025")

    # Check if API keys are set before allowing research
    if not st.session_state.api_keys_set and not check_api_keys():
        st.warning("Please set your API keys in the sidebar before starting research.")

    # Start research button
    if st.button("Start Deep Research", type="primary",
                 disabled=not (st.session_state.api_keys_set or check_api_keys())):
        if not query:
            st.warning("Please enter a research topic.")
        else:
            st.session_state.research_completed = False
            st.session_state.search_plan = None
            st.session_state.search_results = None
            st.session_state.report = None

            # Create tabs for the research process
            tab1, tab2, tab3, tab4 = st.tabs(["Research Plan", "Search Results", "Report", "Resources"])

            with tab1:
                st.header("Research Strategy")
                # Run async functions using asyncio
                search_plan, web_searches, video_searches, strategy = asyncio.run(plan_searches(query))
                st.session_state.search_plan = search_plan

                st.markdown(f"**Overall Strategy:**")
                st.write(strategy)

                st.markdown("### Planned Searches")

                # Display web searches
                st.subheader(f"Web Searches ({len(web_searches)})")
                for i, search in enumerate(web_searches):
                    with st.expander(f"{search.query} (Priority: {search.priority})"):
                        st.write(f"**Reason:** {search.reason}")

                # Display video searches
                st.subheader(f"Video Searches ({len(video_searches)})")
                for i, search in enumerate(video_searches):
                    with st.expander(f"{search.query} (Priority: {search.priority})"):
                        st.write(f"**Reason:** {search.reason}")

            with tab2:
                st.header("Search Results")
                # Perform the searches
                search_results = asyncio.run(perform_searches(st.session_state.search_plan))
                st.session_state.search_results = search_results

                # Group results by type
                web_results = [r for r in search_results if r["type"] == "web"]
                video_results = [r for r in search_results if r["type"] == "video"]

                # Display web search results
                st.subheader("Web Research Findings")
                for i, res in enumerate(web_results):
                    with st.expander(f"{res['query']} (Priority: {res['priority']})"):
                        st.markdown(f"**Research Objective:** {res['reason']}")
                        st.markdown("**Findings:**")
                        st.markdown(res['result'])

                # Display video search results
                st.subheader("Video Research Findings")
                for i, res in enumerate(video_results):
                    with st.expander(f"{res['query']} (Priority: {res['priority']})"):
                        st.markdown(f"**Selection Purpose:** {res['reason']}")
                        st.markdown("**Available Content:**")
                        st.markdown(res['result'])

            with tab3:
                st.header("Comprehensive Research Report")
                # Generate the report
                report = asyncio.run(write_report(query, st.session_state.search_results))
                st.session_state.report = report

                # Display report summary
                st.subheader("Executive Summary")
                st.markdown(report.short_summary)

                # Display full report
                st.subheader("Full Report")
                st.markdown(report.markdown_report)

                # Download button for the report
                st.download_button(
                    label="Download Report as Markdown",
                    data=report.markdown_report,
                    file_name="research_report.md",
                    mime="text/markdown"
                )

            with tab4:
                st.header("Key Resources")

                # Display key insights
                st.subheader("Key Insights")
                for i, insight in enumerate(st.session_state.report.key_insights, 1):
                    st.markdown(f"{i}. {insight}")

                # Display recommended videos
                st.subheader("Recommended Videos")
                for video in st.session_state.report.recommended_videos:
                    with st.expander(video.title):
                        st.markdown(f"**Creator:** {video.creator}")
                        st.markdown(f"**Link:** [{video.title}]({video.link})")
                        st.markdown(f"**Description:** {video.description}")

                # Display follow-up questions
                st.subheader("Further Research Questions")
                for i, question in enumerate(st.session_state.report.follow_up_questions, 1):
                    st.markdown(f"{i}. {question}")

            st.session_state.research_completed = True

    # Display previous research results if available
    elif st.session_state.get('research_completed', False):
        tab1, tab2, tab3, tab4 = st.tabs(["Research Plan", "Search Results", "Report", "Resources"])

        with tab1:
            st.header("Research Strategy")
            # Extract from session state
            search_plan = st.session_state.search_plan
            web_searches = [s for s in search_plan if s.search_type == 'web']
            video_searches = [s for s in search_plan if s.search_type == 'video']

            st.markdown("### Planned Searches")

            # Display web searches
            st.subheader(f"Web Searches ({len(web_searches)})")
            for i, search in enumerate(web_searches):
                with st.expander(f"{search.query} (Priority: {search.priority})"):
                    st.write(f"**Reason:** {search.reason}")

            # Display video searches
            st.subheader(f"Video Searches ({len(video_searches)})")
            for i, search in enumerate(video_searches):
                with st.expander(f"{search.query} (Priority: {search.priority})"):
                    st.write(f"**Reason:** {search.reason}")

        with tab2:
            st.header("Search Results")
            # Extract from session state
            search_results = st.session_state.search_results

            # Group results by type
            web_results = [r for r in search_results if r["type"] == "web"]
            video_results = [r for r in search_results if r["type"] == "video"]

            # Display web search results
            st.subheader("Web Research Findings")
            for i, res in enumerate(web_results):
                with st.expander(f"{res['query']} (Priority: {res['priority']})"):
                    st.markdown(f"**Research Objective:** {res['reason']}")
                    st.markdown("**Findings:**")
                    st.markdown(res['result'])

            # Display video search results
            st.subheader("Video Research Findings")
            for i, res in enumerate(video_results):
                with st.expander(f"{res['query']} (Priority: {res['priority']})"):
                    st.markdown(f"**Selection Purpose:** {res['reason']}")
                    st.markdown("**Available Content:**")
                    st.markdown(res['result'])

        with tab3:
            st.header("Comprehensive Research Report")
            # Extract from session state
            report = st.session_state.report

            # Display report summary
            st.subheader("Executive Summary")
            st.markdown(report.short_summary)

            # Display full report
            st.subheader("Full Report")
            st.markdown(report.markdown_report)

            # Download button for the report
            st.download_button(
                label="Download Report as Markdown",
                data=report.markdown_report,
                file_name="research_report.md",
                mime="text/markdown"
            )

        with tab4:
            st.header("Key Resources")

            # Display key insights
            st.subheader("Key Insights")
            for i, insight in enumerate(st.session_state.report.key_insights, 1):
                st.markdown(f"{i}. {insight}")

            # Display recommended videos
            st.subheader("Recommended Videos")
            for video in st.session_state.report.recommended_videos:
                with st.expander(video.title):
                    st.markdown(f"**Creator:** {video.creator}")
                    st.markdown(f"**Link:** [{video.title}]({video.link})")
                    st.markdown(f"**Description:** {video.description}")

            # Display follow-up questions
            st.subheader("Further Research Questions")
            for i, question in enumerate(st.session_state.report.follow_up_questions, 1):
                st.markdown(f"{i}. {question}")


if __name__ == "__main__":
    main()