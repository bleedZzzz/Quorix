"""Literature discovery service querying open academic repositories."""

from __future__ import annotations

import xml.etree.ElementTree as ET

import httpx

from app.schemas.job import DiscoverySearchResult


class DiscoveryService:
    """Queries open scientific indexes (arXiv, OpenAlex) for paper discovery."""

    async def search_arxiv(self, query: str, max_results: int = 10) -> list[DiscoverySearchResult]:
        url = "http://export.arxiv.org/api/query"
        params = {
            "search_query": f"all:{query}",
            "start": 0,
            "max_results": max_results,
        }

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(url, params=params)
                if resp.status_code != 200:
                    return []

                root = ET.fromstring(resp.content)
                ns = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}

                results: list[DiscoverySearchResult] = []
                for entry in root.findall("atom:entry", ns):
                    title_elem = entry.find("atom:title", ns)
                    summary_elem = entry.find("atom:summary", ns)
                    id_elem = entry.find("atom:id", ns)
                    published_elem = entry.find("atom:published", ns)

                    title = title_elem.text.strip().replace("\n", " ") if title_elem is not None and title_elem.text else "Untitled"
                    abstract = summary_elem.text.strip() if summary_elem is not None and summary_elem.text else ""
                    raw_id = id_elem.text.strip() if id_elem is not None and id_elem.text else ""
                    arxiv_id = raw_id.split("/abs/")[-1] if "/abs/" in raw_id else raw_id

                    year = None
                    if published_elem is not None and published_elem.text:
                        year = int(published_elem.text[:4])

                    authors = []
                    for author_elem in entry.findall("atom:author", ns):
                        name_elem = author_elem.find("atom:name", ns)
                        if name_elem is not None and name_elem.text:
                            authors.append(name_elem.text.strip())

                    pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf" if arxiv_id else None

                    results.append(
                        DiscoverySearchResult(
                            title=title,
                            abstract=abstract,
                            year=year,
                            venue="arXiv",
                            arxiv_id=arxiv_id,
                            authors=authors,
                            pdf_url=pdf_url,
                            source="arxiv",
                        )
                    )
                return results
        except Exception:
            return []

    async def search(self, query: str, max_results: int = 10) -> list[DiscoverySearchResult]:
        """Aggregate discovery search."""
        return await self.search_arxiv(query=query, max_results=max_results)
