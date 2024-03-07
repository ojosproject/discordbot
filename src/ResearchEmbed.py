# ResearchEmbed.py
# Ojos Project
# 
# Embeds centered around `dict`s and limits.
# Refer to the Discord documentation:
# https://discord.com/developers/docs/resources/channel#embed-object
from discord import Embed

class ResearchEmbed:
    def __init__(self, papers: list[dict]) -> None:
        self._raw_data = {
            "title": "Research Papers",
            "description": "These are the research papers for the Research team.",
            "fields": []
        }

        self._add_papers(papers)

    def _add_papers(self, papers: list[dict]) -> None:
        # recursive function
        sorted_papers = sorted(papers, key=lambda x: x['id'], reverse=True)
        
        for paper in sorted_papers:
            # title
            self._raw_data['fields'].append(
                {
                    "name": "Title",
                    "value": f"[{paper['title'][:35]}... (#{paper['id']})]({paper['url']})",
                    "inline": True
                }
            )

            assigned = "Nobody"

            if paper['assigned_to']:
                assigned = f"<@{paper['assigned_to']}>"

            self._raw_data['fields'].append(
                {
                    "name": "Assigned to",
                    "value": assigned,
                    "inline": True
                }
            )

            finished = ":x: No"
            if paper['notes'] and paper['summary'] and paper['submitted']:
                finished = ":white_check_mark: Yes!"

            self._raw_data['fields'].append(
                {
                    "name": "Finished?",
                    "value": finished,
                    "inline": True
                }
            )

            self._raw_data['fields'].append(
                {
                    "name": " ",
                    "value": " ",
                    "inline": False
                }
            )

            if len(self._raw_data['fields']) >= 22:
                break

    def discord_embed(self) -> Embed:
        return Embed.from_dict(self._raw_data)
