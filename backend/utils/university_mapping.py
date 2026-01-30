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
    # Additional US Universities
    "yale": {
        "official_name": "Yale University",
        "variations": ["Yale", "Yale U"],
        "domain": "yale.edu",
        "faculty_urls": []
    },
    "usc": {
        "official_name": "University of Southern California",
        "variations": ["USC", "Southern California", "U of SC"],
        "domain": "usc.edu",
        "faculty_urls": []
    },
    "upenn": {
        "official_name": "University of Pennsylvania",
        "variations": ["UPenn", "Penn", "U Penn", "Pennsylvania"],
        "domain": "upenn.edu",
        "faculty_urls": []
    },
    "brown": {
        "official_name": "Brown University",
        "variations": ["Brown", "Brown U"],
        "domain": "brown.edu",
        "faculty_urls": []
    },
    "duke": {
        "official_name": "Duke University",
        "variations": ["Duke", "Duke U"],
        "domain": "duke.edu",
        "faculty_urls": []
    },
    "jhu": {
        "official_name": "Johns Hopkins University",
        "variations": ["JHU", "Johns Hopkins", "Hopkins"],
        "domain": "jhu.edu",
        "faculty_urls": []
    },
    "northwestern": {
        "official_name": "Northwestern University",
        "variations": ["Northwestern", "NU"],
        "domain": "northwestern.edu",
        "faculty_urls": []
    },
    "purdue": {
        "official_name": "Purdue University",
        "variations": ["Purdue", "Purdue U"],
        "domain": "purdue.edu",
        "faculty_urls": []
    },
    "ut_austin": {
        "official_name": "University of Texas at Austin",
        "variations": ["UT Austin", "Texas", "UT", "U Texas"],
        "domain": "utexas.edu",
        "faculty_urls": []
    },
    "wisconsin": {
        "official_name": "University of Wisconsin-Madison",
        "variations": ["UW Madison", "Wisconsin", "UW-Madison"],
        "domain": "wisc.edu",
        "faculty_urls": []
    },
    "umd": {
        "official_name": "University of Maryland",
        "variations": ["UMD", "Maryland", "U Maryland"],
        "domain": "umd.edu",
        "faculty_urls": []
    },
    "uva": {
        "official_name": "University of Virginia",
        "variations": ["UVA", "Virginia", "U Virginia"],
        "domain": "virginia.edu",
        "faculty_urls": []
    },
    "rice": {
        "official_name": "Rice University",
        "variations": ["Rice", "Rice U"],
        "domain": "rice.edu",
        "faculty_urls": []
    },
    "unc": {
        "official_name": "University of North Carolina at Chapel Hill",
        "variations": ["UNC", "Chapel Hill", "North Carolina"],
        "domain": "unc.edu",
        "faculty_urls": []
    },
    "osu": {
        "official_name": "Ohio State University",
        "variations": ["OSU", "Ohio State"],
        "domain": "osu.edu",
        "faculty_urls": []
    },
    "psu": {
        "official_name": "Pennsylvania State University",
        "variations": ["Penn State", "PSU"],
        "domain": "psu.edu",
        "faculty_urls": []
    },
    "asu": {
        "official_name": "Arizona State University",
        "variations": ["ASU", "Arizona State"],
        "domain": "asu.edu",
        "faculty_urls": []
    },
    # International Universities
    "imperial": {
        "official_name": "Imperial College London",
        "variations": ["Imperial", "Imperial College", "ICL"],
        "domain": "imperial.ac.uk",
        "faculty_urls": []
    },
    "ucl": {
        "official_name": "University College London",
        "variations": ["UCL"],
        "domain": "ucl.ac.uk",
        "faculty_urls": []
    },
    "edinburgh": {
        "official_name": "University of Edinburgh",
        "variations": ["Edinburgh", "UoE"],
        "domain": "ed.ac.uk",
        "faculty_urls": []
    },
    "tsinghua": {
        "official_name": "Tsinghua University",
        "variations": ["Tsinghua", "THU"],
        "domain": "tsinghua.edu.cn",
        "faculty_urls": []
    },
    "peking": {
        "official_name": "Peking University",
        "variations": ["Peking", "PKU", "Beijing University"],
        "domain": "pku.edu.cn",
        "faculty_urls": []
    },
    "nus": {
        "official_name": "National University of Singapore",
        "variations": ["NUS", "Singapore"],
        "domain": "nus.edu.sg",
        "faculty_urls": []
    },
    "hku": {
        "official_name": "University of Hong Kong",
        "variations": ["HKU", "Hong Kong"],
        "domain": "hku.hk",
        "faculty_urls": []
    },
    "epfl": {
        "official_name": "EPFL",
        "variations": ["EPFL", "Swiss Federal Institute of Technology Lausanne"],
        "domain": "epfl.ch",
        "faculty_urls": []
    },
    "mpi": {
        "official_name": "Max Planck Institute",
        "variations": ["MPI", "Max Planck"],
        "domain": "mpg.de",
        "faculty_urls": []
    },
    "tum": {
        "official_name": "Technical University of Munich",
        "variations": ["TUM", "TU Munich"],
        "domain": "tum.de",
        "faculty_urls": []
    },
    "mcgill": {
        "official_name": "McGill University",
        "variations": ["McGill"],
        "domain": "mcgill.ca",
        "faculty_urls": []
    },
    "waterloo": {
        "official_name": "University of Waterloo",
        "variations": ["Waterloo", "UWaterloo"],
        "domain": "uwaterloo.ca",
        "faculty_urls": []
    },
    "ubc": {
        "official_name": "University of British Columbia",
        "variations": ["UBC", "British Columbia"],
        "domain": "ubc.ca",
        "faculty_urls": []
    },
    "melbourne": {
        "official_name": "University of Melbourne",
        "variations": ["Melbourne", "UniMelb"],
        "domain": "unimelb.edu.au",
        "faculty_urls": []
    },
    "sydney": {
        "official_name": "University of Sydney",
        "variations": ["Sydney", "USYD"],
        "domain": "sydney.edu.au",
        "faculty_urls": []
    },
    "anu": {
        "official_name": "Australian National University",
        "variations": ["ANU"],
        "domain": "anu.edu.au",
        "faculty_urls": []
    },
    "tokyo": {
        "official_name": "University of Tokyo",
        "variations": ["Tokyo", "UTokyo", "Todai"],
        "domain": "u-tokyo.ac.jp",
        "faculty_urls": []
    },
    "kaist": {
        "official_name": "KAIST",
        "variations": ["KAIST", "Korea Advanced Institute"],
        "domain": "kaist.ac.kr",
        "faculty_urls": []
    },
    "seoul": {
        "official_name": "Seoul National University",
        "variations": ["SNU", "Seoul National"],
        "domain": "snu.ac.kr",
        "faculty_urls": []
    },
    "technion": {
        "official_name": "Technion",
        "variations": ["Technion", "Israel Institute of Technology"],
        "domain": "technion.ac.il",
        "faculty_urls": []
    },
    "tel_aviv": {
        "official_name": "Tel Aviv University",
        "variations": ["TAU", "Tel Aviv"],
        "domain": "tau.ac.il",
        "faculty_urls": []
    },
    "amsterdam": {
        "official_name": "University of Amsterdam",
        "variations": ["UvA", "Amsterdam"],
        "domain": "uva.nl",
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
