import json
import os
import requests
from agents import function_tool


@function_tool
def search_tool(query: str) -> str:
    """
    Useful to search the internet about a given topic and return the results
    """
    top_result_to_return = 10
    url = "https://google.serper.dev/search"
    payload = json.dumps({"q": query})
    headers = {
        'X-API-KEY': os.environ['SERPER_API_KEY'],
        'content-type': 'application/json'
    }

    try:
        response = requests.request("POST", url, headers=headers, data=payload, timeout=10)
        response.raise_for_status()

        data = response.json()
        if 'organic' not in data or not data['organic']:
            return "No organic search results found. Try refining your query."

        results = data['organic']
        string = []
        for result in results[:top_result_to_return]:
            try:
                snippet = result.get('snippet', 'No snippet available')
                title = result.get('title', 'No title available')
                link = result.get('link', 'No link available')

                string.append('\n'.join([
                    f"Title: {title}",
                    f"Link: {link}",
                    f"Snippet: {snippet}",
                    "\n--------------"
                ]))
            except KeyError:
                continue

        return '\n'.join(string)

    except requests.exceptions.RequestException as e:
        return f"Search error: {str(e)}"


@function_tool
def video_search_tool(query: str) -> str:
    """
    Search for video content related to a given topic and return the results.
    """
    top_result_to_return = 8  # Increased to get more options for filtering
    url = "https://google.serper.dev/search"
    payload = json.dumps({"q": query, "type": "videos"})
    headers = {
        'X-API-KEY': os.environ['SERPER_API_KEY'],
        'content-type': 'application/json'
    }

    try:
        response = requests.request("POST", url, headers=headers, data=payload, timeout=10)
        response.raise_for_status()

        data = response.json()
        if 'videos' not in data or not data['videos']:
            return "No video results found. Try refining your query."

        results = data['videos']
        string = []
        for result in results[:top_result_to_return]:
            try:
                # Extract duration and convert to seconds for filtering
                duration_str = result.get('duration', '0:00')

                # Skip videos less than 3 minutes (180 seconds)
                minutes, seconds = 0, 0
                if ':' in duration_str:
                    parts = duration_str.split(':')
                    if len(parts) == 2:
                        minutes, seconds = int(parts[0]), int(parts[1])
                    elif len(parts) == 3:
                        hours, minutes, seconds = int(parts[0]), int(parts[1]), int(parts[2])
                        minutes += hours * 60

                total_seconds = minutes * 60 + seconds
                if total_seconds < 180:  # Skip videos shorter than 3 minutes
                    continue

                # Include all available fields in the output
                output_elements = [
                    f"Title: {result.get('title', 'No title available')}",
                    f"Link: {result.get('link', 'No link available')}",
                    f"Channel: {result.get('channel', 'Unknown channel')}",
                    f"Duration: {duration_str}",
                    f"Published: {result.get('date', 'Unknown date')}",
                    f"Snippet: {result.get('snippet', 'No snippet available')}",
                    "\n--------------"
                ]

                string.append('\n'.join(output_elements))
            except KeyError:
                continue

        return '\n'.join(string)

    except requests.exceptions.RequestException as e:
        return f"Video search error: {str(e)}"