"""
Mapping of university abbreviations/common names to official names and domains.
This helps with searching across different APIs that may use different naming conventions.
"""

UNIVERSITY_MAPPINGS = {
    # Carnegie Mellon
    "cmu": {
        "official_name": "Carnegie Mellon University",
        "variations": ["Carnegie Mellon", "CMU", "Carnegie-Mellon"],
        "domain": "cmu.edu",
        "faculty_urls": [
            "https://www.cs.cmu.edu/people/faculty",
            "https://www.ml.cmu.edu/people/",
            "https://www.lti.cs.cmu.edu/people/faculty",
        ]
    },
    "mit": {
        "official_name": "Massachusetts Institute of Technology",
        "variations": ["MIT", "Mass. Institute of Technology"],
        "domain": "mit.edu",
        "faculty_urls": [
            "https://www.csail.mit.edu/people",
            "https://www.eecs.mit.edu/people/faculty-advisors",
        ]
    },
    "stanford": {
        "official_name": "Stanford University",
        "variations": ["Stanford", "Stanford U"],
        "domain": "stanford.edu",
        "faculty_urls": [
            "https://cs.stanford.edu/people/faculty",
            "https://ai.stanford.edu/people/",
        ]
    },
    "berkeley": {
        "official_name": "University of California, Berkeley",
        "variations": ["UC Berkeley", "Berkeley", "Cal", "UCB"],
        "domain": "berkeley.edu",
        "faculty_urls": [
            "https://www2.eecs.berkeley.edu/Faculty/Lists/CS/faculty.html",
        ]
    },
    "harvard": {
        "official_name": "Harvard University",
        "variations": ["Harvard", "Harvard U"],
        "domain": "harvard.edu",
        "faculty_urls": [
            "https://seas.harvard.edu/computer-science/people",
        ]
    },
    "princeton": {
        "official_name": "Princeton University",
        "variations": ["Princeton", "Princeton U"],
        "domain": "princeton.edu",
        "faculty_urls": [
            "https://www.cs.princeton.edu/people/faculty",
        ]
    },
    "cornell": {
        "official_name": "Cornell University",
        "variations": ["Cornell", "Cornell U"],
        "domain": "cornell.edu",
        "faculty_urls": [
            "https://www.cs.cornell.edu/people/faculty",
        ]
    },
    "uw": {
        "official_name": "University of Washington",
        "variations": ["UW", "U Washington", "Washington"],
        "domain": "washington.edu",
        "faculty_urls": [
            "https://www.cs.washington.edu/people/faculty",
        ]
    },
    "gatech": {
        "official_name": "Georgia Institute of Technology",
        "variations": ["Georgia Tech", "GT", "GaTech"],
        "domain": "gatech.edu",
        "faculty_urls": [
            "https://www.cc.gatech.edu/people/faculty",
        ]
    },
    "uiuc": {
        "official_name": "University of Illinois Urbana-Champaign",
        "variations": ["UIUC", "Illinois", "U of I"],
        "domain": "illinois.edu",
        "faculty_urls": [
            "https://cs.illinois.edu/about/people/faculty",
        ]
    },
    "umich": {
        "official_name": "University of Michigan",
        "variations": ["UMich", "Michigan", "U Michigan"],
        "domain": "umich.edu",
        "faculty_urls": [
            "https://cse.engin.umich.edu/people/faculty/",
        ]
    },
    "nyu": {
        "official_name": "New York University",
        "variations": ["NYU", "New York U"],
        "domain": "nyu.edu",
        "faculty_urls": [
            "https://cs.nyu.edu/people/faculty.html",
        ]
    },
    "columbia": {
        "official_name": "Columbia University",
        "variations": ["Columbia", "Columbia U"],
        "domain": "columbia.edu",
        "faculty_urls": [
            "https://www.cs.columbia.edu/people/faculty/",
        ]
    },
    "ucsd": {
        "official_name": "University of California, San Diego",
        "variations": ["UCSD", "UC San Diego"],
        "domain": "ucsd.edu",
        "faculty_urls": [
            "https://cse.ucsd.edu/people/faculty",
        ]
    },
    "ucla": {
        "official_name": "University of California, Los Angeles",
        "variations": ["UCLA", "UC Los Angeles"],
        "domain": "ucla.edu",
        "faculty_urls": [
            "https://www.cs.ucla.edu/people/faculty/",
        ]
    },
    "eth": {
        "official_name": "ETH Zurich",
        "variations": ["ETH", "ETH Zürich", "Swiss Federal Institute of Technology"],
        "domain": "ethz.ch",
        "faculty_urls": []
    },
    "oxford": {
        "official_name": "University of Oxford",
        "variations": ["Oxford", "Oxford U"],
        "domain": "ox.ac.uk",
        "faculty_urls": []
    },
    "cambridge": {
        "official_name": "University of Cambridge",
        "variations": ["Cambridge", "Cambridge U"],
        "domain": "cam.ac.uk",
        "faculty_urls": []
    },
    "toronto": {
        "official_name": "University of Toronto",
        "variations": ["UofT", "Toronto", "U Toronto"],
        "domain": "utoronto.ca",
        "faculty_urls": []
    },
}


def normalize_university(name: str) -> dict | None:
    """
    Given a university name or abbreviation, return the mapping info.
    Returns None if not found.
    """
    name_lower = name.lower().strip()

    # Direct match on key
    if name_lower in UNIVERSITY_MAPPINGS:
        return UNIVERSITY_MAPPINGS[name_lower]

    # Search through variations
    for key, info in UNIVERSITY_MAPPINGS.items():
        if name_lower == info["official_name"].lower():
            return info
        for variation in info["variations"]:
            if name_lower == variation.lower():
                return info

    # Partial match - be careful with this
    for key, info in UNIVERSITY_MAPPINGS.items():
        if name_lower in info["official_name"].lower():
            return info
        if info["official_name"].lower() in name_lower:
            return info

    # Not found - return a basic structure
    return {
        "official_name": name,
        "variations": [name],
        "domain": None,
        "faculty_urls": []
    }


def get_university_search_terms(name: str) -> list[str]:
    """
    Get all variations of university name for searching.
    """
    info = normalize_university(name)
    if info:
        terms = [info["official_name"]] + info.get("variations", [])
        return list(set(terms))
    return [name]
