from agents import Agent
from models.schemas import ReportData

writer_agent = Agent(
    name="DeepResearchWriter",
    instructions="""
    "You are a senior researcher tasked with writing a cohesive report for a research query. "
    "You will be provided with the original query, and some initial research done by a research assistant.\n"
    "You should first come up with an outline for the report that describes the structure and "
    "flow of the report. Then, generate the report and return that as your final output.\n"
    "The final output should be in markdown format, and it should be lengthy and detailed. Aim "
    "for 5-10 pages of content, at least 3000 words."
""",
model="gpt-4o",
output_type=ReportData
)