# AI Deep Research Assistant

A powerful multi-agent system for comprehensive research on any topic, built using the OpenAI Agent SDK and Streamlit.

## Overview

This project orchestrates multiple specialized AI agents to produce in-depth research reports:

1. **Planning Agent** - Creates a strategic research plan with diverse search queries
2. **Web Search Agent** - Performs web searches and analyzes results
3. **Video Search Agent** - Identifies high-quality educational videos
4. **Writer Agent** - Synthesizes findings into a comprehensive report

## Features

- Parallel execution of multiple search queries for faster results
- Seamless orchestration of specialized agents
- Beautiful Streamlit interface with tabs for each research stage
- Downloadable comprehensive research reports with citations
- Video recommendations from trusted sources

## System Workflow

```mermaid
flowchart TD
    %% Main nodes
    User(User) -->|Enter Research Query| StreamlitApp[Streamlit Application]
    StreamlitApp -->|Send Query| ResearchProcess[Research Process]
    
    subgraph ResearchProcess[Research Process]
        Query[Research Query] -->|Analyze Query| PlannerAgent
        
        PlannerAgent[Planner Agent\nGPT-4o-mini] -->|Generate Search Plan| SearchPlan
        
        SearchPlan[Search Plan\n4-7 Search Queries] -->|Web Searches| WebSearches
        SearchPlan -->|Video Searches| VideoSearches
        
        subgraph WebSearches[Web Search Process]
            WebSearchItem[Web Search Items] -->|Execute Searches| WebSearchAgent
            WebSearchAgent[Web Search Agent\nGPT-4o-mini] -->|Call Search Tool| SerperAPI[(Serper API)]
            SerperAPI -->|Return Results| WebSearchResults[Web Search Results]
        end
        
        subgraph VideoSearches[Video Search Process]
            VideoSearchItem[Video Search Items] -->|Execute Searches| VideoSearchAgent
            VideoSearchAgent[Video Search Agent\nGPT-4o-mini] -->|Call Video Search Tool| SerperAPI2[(Serper API)]
            VideoSearchAgent -->|Check Date| CurrentDate[Current Date Tool]
            SerperAPI2 -->|Return Results| VideoSearchResults[Video Search Results]
        end
        
        WebSearchResults -->|Combine Results| AllSearchResults[All Search Results]
        VideoSearchResults -->|Combine Results| AllSearchResults
        
        AllSearchResults -->|Synthesize Information| WriterAgent[Writer Agent\nGPT-4o]
        WriterAgent -->|Generate Report| ResearchReport[Comprehensive Report]
    end
    
    ResearchReport -->|Display in UI| ResultDisplay[Result Display]
    
    subgraph ResultDisplay[Result Display]
        Tab1[Research Plan Tab]
        Tab2[Search Results Tab]
        Tab3[Report Tab] -->|Download Option| DownloadReport[Download Report]
        Tab4[Resources Tab]
    end
    
    ResultDisplay -->|Show to User| User
    
    %% Styling
    classDef agent fill:#d0e0ff,stroke:#3080ff,stroke-width:2px
    classDef tool fill:#ffe0d0,stroke:#ff8030,stroke-width:2px
    classDef data fill:#e0ffd0,stroke:#80ff30,stroke-width:2px
    classDef ui fill:#ffd0e0,stroke:#ff30a0,stroke-width:2px
    
    class PlannerAgent,WebSearchAgent,VideoSearchAgent,WriterAgent agent
    class SerperAPI,SerperAPI2,CurrentDate tool
    class Query,SearchPlan,WebSearchResults,VideoSearchResults,AllSearchResults,ResearchReport data
    class StreamlitApp,User,ResultDisplay,Tab1,Tab2,Tab3,Tab4,DownloadReport ui
```

## Project Structure

```
research_app/
├── app.py               # Main Streamlit application
├── requirements.txt     # Project dependencies
├── tools/               # Search and utility tools
│   ├── __init__.py      
│   ├── search_tools.py  # Web and video search tools
│   └── date_tools.py    # Date-related tools
├── workers/             # Agent definitions
│   ├── __init__.py      
│   ├── planner.py       # Planning agent
│   ├── web_search.py    # Web search agent
│   ├── video_search.py  # Video search agent
│   └── writer.py        # Report writer agent
└── models/              # Data models
    ├── __init__.py      
    └── schemas.py       # Pydantic schemas
```

## Installation

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Set up your API keys:
   - OpenAI API key for agent functionality
   - Serper API key for web search capabilities

## Usage

Run the application:
```
streamlit run app.py
```

In the web interface:
1. Enter your API keys in the sidebar (if not set in environment)
2. Enter your research topic
3. Click "Start Deep Research"
4. Explore the results in the different tabs:
   - Research Plan - View the search strategy
   - Search Results - View findings from web and video searches  
   - Report - See the comprehensive research report
   - Resources - Explore key insights and recommended videos

## Requirements

- Python 3.8+
- Streamlit
- Pydantic
- OpenAI Agent SDK
- Python-dotenv
- Requests

