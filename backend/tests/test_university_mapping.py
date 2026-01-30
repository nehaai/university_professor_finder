"""
Tests for university mapping utilities.
"""

import pytest
from utils.university_mapping import normalize_university, get_university_search_terms


class TestNormalizeUniversity:
    """Test suite for normalize_university function."""

    def test_direct_key_match(self):
        """Direct key match should work."""
        result = normalize_university("cmu")
        assert result["official_name"] == "Carnegie Mellon University"
        assert "CMU" in result["variations"]

    def test_case_insensitive(self):
        """Matching should be case insensitive."""
        result = normalize_university("MIT")
        assert result["official_name"] == "Massachusetts Institute of Technology"

        result = normalize_university("mit")
        assert result["official_name"] == "Massachusetts Institute of Technology"

    def test_variation_match(self):
        """Should match on variations."""
        result = normalize_university("UC Berkeley")
        assert result["official_name"] == "University of California, Berkeley"

    def test_official_name_match(self):
        """Should match on official name."""
        result = normalize_university("Stanford University")
        assert result["official_name"] == "Stanford University"

    def test_unknown_university_returns_basic_structure(self):
        """Unknown university should return basic structure."""
        result = normalize_university("Unknown University XYZ")
        assert result["official_name"] == "Unknown University XYZ"
        assert result["domain"] is None

    def test_georgia_tech_variations(self):
        """Georgia Tech should match various abbreviations."""
        for name in ["Georgia Tech", "GT", "GaTech", "gatech"]:
            result = normalize_university(name)
            assert result["official_name"] == "Georgia Institute of Technology"

    def test_uc_schools(self):
        """UC schools should resolve correctly."""
        result = normalize_university("UCLA")
        assert result["official_name"] == "University of California, Los Angeles"

        result = normalize_university("UCSD")
        assert result["official_name"] == "University of California, San Diego"


class TestGetUniversitySearchTerms:
    """Test suite for get_university_search_terms function."""

    def test_returns_multiple_terms(self):
        """Should return multiple search terms."""
        terms = get_university_search_terms("cmu")
        assert "Carnegie Mellon University" in terms
        assert "CMU" in terms

    def test_removes_duplicates(self):
        """Should not have duplicate terms."""
        terms = get_university_search_terms("MIT")
        assert len(terms) == len(set(terms))

    def test_unknown_university_returns_original(self):
        """Unknown university should return original name."""
        terms = get_university_search_terms("Unknown Uni")
        assert "Unknown Uni" in terms

    def test_international_universities(self):
        """International universities should resolve."""
        terms = get_university_search_terms("ETH")
        assert "ETH Zurich" in terms

        terms = get_university_search_terms("Oxford")
        assert "University of Oxford" in terms
