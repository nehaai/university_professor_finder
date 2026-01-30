"""
University Lab Page Scraper
Attempts to find and scrape lab pages to get student information.
This is the least reliable part - scraping can break when sites change.
"""

import httpx
from bs4 import BeautifulSoup
from typing import Optional
import asyncio
import re
from urllib.parse import urljoin, urlparse

from utils.cache import cached


# Common patterns for lab/research group pages
LAB_PAGE_PATTERNS = [
    r'/people',
    r'/team',
    r'/members',
    r'/students',
    r'/group',
    r'/lab',
]

# Common patterns for identifying students
STUDENT_PATTERNS = [
    r'ph\.?d\.?\s*(student|candidate)',
    r'doctoral\s*(student|candidate)',
    r'graduate\s*student',
    r'research\s*assistant',
    r'postdoc',
    r'post-doc',
    r'postdoctoral',
    r'master\'?s?\s*student',
    r'ms\s*student',
]

# User agent to be polite
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; UniversityProfessorFinder/1.0; Academic Research Tool)"
}


class LabScraper:
    def __init__(self):
        self._last_request_time = 0
        self._request_delay = 2.0  # Be very polite - 2 seconds between requests

    async def _rate_limit(self):
        """Ensure we don't overwhelm servers."""
        import time
        current_time = time.time()
        elapsed = current_time - self._last_request_time
        if elapsed < self._request_delay:
            await asyncio.sleep(self._request_delay - elapsed)
        self._last_request_time = time.time()

    async def _fetch_page(self, url: str) -> Optional[str]:
        """Fetch HTML content from a URL."""
        await self._rate_limit()

        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            try:
                response = await client.get(url, headers=HEADERS)
                response.raise_for_status()
                return response.text
            except Exception as e:
                print(f"Failed to fetch {url}: {e}")
                return None

    def _extract_people_links(self, html: str, base_url: str) -> list[dict]:
        """
        Extract links that might lead to people/team pages.
        """
        soup = BeautifulSoup(html, 'lxml')
        people_links = []

        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            text = link.get_text(strip=True).lower()

            # Check if link text or URL suggests a people page
            is_people_link = any(
                pattern in href.lower() or pattern.strip('/') in text
                for pattern in LAB_PAGE_PATTERNS
            )

            if is_people_link:
                full_url = urljoin(base_url, href)
                people_links.append({
                    'url': full_url,
                    'text': link.get_text(strip=True)
                })

        return people_links

    def _extract_students_from_page(self, html: str, base_url: str) -> list[dict]:
        """
        Extract student information from a page.
        This is heuristic-based and may not work on all sites.
        """
        soup = BeautifulSoup(html, 'lxml')
        students = []

        # Common structures for listing people:
        # 1. List items with person info
        # 2. Divs/cards with person info
        # 3. Tables with person info

        # Strategy 1: Look for elements with student-related keywords
        text_content = soup.get_text()

        # Find sections that mention students
        student_section_found = any(
            re.search(pattern, text_content, re.IGNORECASE)
            for pattern in STUDENT_PATTERNS
        )

        if not student_section_found:
            return students

        # Strategy 2: Look for common person card patterns
        person_elements = []

        # Try common class names for person cards
        for class_pattern in ['person', 'member', 'student', 'team-member', 'people', 'profile']:
            person_elements.extend(soup.find_all(class_=re.compile(class_pattern, re.I)))

        # Also try looking at list items within certain sections
        for section in soup.find_all(['section', 'div', 'ul']):
            section_text = section.get_text().lower()
            if any(re.search(p, section_text, re.I) for p in STUDENT_PATTERNS):
                # This section mentions students, extract names from it
                person_elements.extend(section.find_all(['li', 'div', 'article']))

        seen_names = set()

        for elem in person_elements:
            # Try to extract person name
            name = None

            # Look for name in headings
            for heading in elem.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'strong', 'b']):
                potential_name = heading.get_text(strip=True)
                # Basic name validation: 2-4 words, starts with capital
                words = potential_name.split()
                if 2 <= len(words) <= 5 and words[0][0].isupper():
                    name = potential_name
                    break

            if not name:
                # Try first link text
                link = elem.find('a')
                if link:
                    potential_name = link.get_text(strip=True)
                    words = potential_name.split()
                    if 2 <= len(words) <= 5:
                        name = potential_name

            if not name:
                continue

            # Avoid duplicates
            if name.lower() in seen_names:
                continue
            seen_names.add(name.lower())

            # Try to determine role
            elem_text = elem.get_text().lower()
            role = None
            for pattern in STUDENT_PATTERNS:
                match = re.search(pattern, elem_text, re.I)
                if match:
                    role = match.group(0).title()
                    break

            # Try to get URL
            person_url = None
            link = elem.find('a', href=True)
            if link:
                person_url = urljoin(base_url, link['href'])

            students.append({
                'name': name,
                'role': role,
                'url': person_url,
                'source': 'lab_website_scrape'
            })

        return students

    @cached(ttl=7200)  # Cache for 2 hours
    async def scrape_lab_for_students(self, lab_url: str) -> list[dict]:
        """
        Given a lab URL, attempt to find and scrape the people/team page
        to extract student information.
        """
        if not lab_url:
            return []

        students = []

        # First, fetch the main lab page
        html = await self._fetch_page(lab_url)
        if not html:
            return []

        # Try to extract students directly from the main page
        students = self._extract_students_from_page(html, lab_url)

        if students:
            return students

        # If no students found, look for people/team page links
        people_links = self._extract_people_links(html, lab_url)

        for link_info in people_links[:3]:  # Limit to avoid too many requests
            page_html = await self._fetch_page(link_info['url'])
            if page_html:
                page_students = self._extract_students_from_page(page_html, link_info['url'])
                students.extend(page_students)

        # Deduplicate by name
        seen = set()
        unique_students = []
        for student in students:
            name_key = student['name'].lower()
            if name_key not in seen:
                seen.add(name_key)
                unique_students.append(student)

        return unique_students

    async def find_lab_url_from_homepage(self, homepage_url: str) -> Optional[str]:
        """
        Given a professor's homepage, try to find their lab/research group URL.
        """
        if not homepage_url:
            return None

        html = await self._fetch_page(homepage_url)
        if not html:
            return None

        soup = BeautifulSoup(html, 'lxml')

        # Look for links mentioning lab, research, group
        lab_keywords = ['lab', 'research group', 'research lab', 'group', 'team']

        for link in soup.find_all('a', href=True):
            link_text = link.get_text(strip=True).lower()
            href = link.get('href', '').lower()

            if any(kw in link_text or kw in href for kw in lab_keywords):
                return urljoin(homepage_url, link['href'])

        return None


# Singleton instance
lab_scraper = LabScraper()
