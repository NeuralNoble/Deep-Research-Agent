from pydantic import BaseModel


class WebSearchItem(BaseModel):
    reason: str
    """Your reasoning for why this search is important to the query."""

    query: str
    """The search term to use for the web search."""

    search_type: str
    """The type of search to perform: 'web' or 'video'."""

    priority: int
    """Priority of this search on a scale of 1-10, with 10 being highest priority."""


class WebSearchPlan(BaseModel):
    searches: list[WebSearchItem]
    """A list of web and video searches to perform to best answer the query."""

    strategy: str
    """The overall search strategy explaining the approach to answering the query."""


class RecommendedVideo(BaseModel):
    title: str
    """Title of the recommended video."""

    link: str
    """Direct clickable link to the video."""

    description: str
    """Brief description of what the video covers and why it's valuable."""

    creator: str
    """Name of the video creator or channel."""


class ReportData(BaseModel):
    short_summary: str
    """A short 2-3 sentence summary of the findings."""

    markdown_report: str
    """The final report in markdown format."""

    recommended_videos: list[RecommendedVideo]
    """List of recommended videos with complete details."""

    follow_up_questions: list[str]
    """Suggested topics to research further."""

    key_insights: list[str]
    """List of the most important takeaways from the research."""