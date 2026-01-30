"""
Tests for relevance scoring utilities.
"""

import pytest
from utils.relevance import (
    should_exclude_paper,
    has_required_keywords,
    calculate_topic_relevance,
    EXCLUDE_KEYWORDS,
    LLM_REQUIRED_KEYWORDS
)


class TestShouldExcludePaper:
    """Test suite for should_exclude_paper function."""

    def test_excludes_biology_papers(self):
        """Should exclude biology-related papers."""
        assert should_exclude_paper("fMRI analysis of brain regions")
        assert should_exclude_paper("Neuroimaging study of hippocampus")
        assert should_exclude_paper("Gene expression in cancer cells")

    def test_excludes_neuroscience_papers(self):
        """Should exclude neuroscience papers."""
        assert should_exclude_paper("Synaptic plasticity in neurons")
        assert should_exclude_paper("EEG signals during sleep")
        assert should_exclude_paper("Cortical activity mapping")

    def test_excludes_materials_science(self):
        """Should exclude materials science papers."""
        assert should_exclude_paper("Polymer synthesis and characterization")
        assert should_exclude_paper("Crystalline structure of nanoparticles")

    def test_allows_cs_papers(self):
        """Should allow computer science papers."""
        assert not should_exclude_paper("Large Language Model Training")
        assert not should_exclude_paper("Neural Network Optimization")
        assert not should_exclude_paper("Machine Learning for NLP")

    def test_allows_ml_papers(self):
        """Should allow machine learning papers."""
        assert not should_exclude_paper("Attention mechanism in transformers")
        assert not should_exclude_paper("Reinforcement learning for robotics")


class TestHasRequiredKeywords:
    """Test suite for has_required_keywords function."""

    def test_llm_topic_requires_keywords(self):
        """LLM topic should require specific keywords."""
        assert has_required_keywords("LLM", "Large Language Model Training")
        assert has_required_keywords("LLM", "GPT and transformer models")
        assert not has_required_keywords("LLM", "Brain imaging study")

    def test_nlp_topic_requires_keywords(self):
        """NLP topic should require specific keywords."""
        assert has_required_keywords("NLP", "Natural Language Processing")
        assert has_required_keywords("NLP", "Text classification with BERT")
        assert not has_required_keywords("NLP", "Ocean temperature analysis")

    def test_non_special_topics_always_pass(self):
        """Non-special topics should always pass."""
        assert has_required_keywords("Machine Learning", "Any title")
        assert has_required_keywords("Robotics", "Any title")


class TestCalculateTopicRelevance:
    """Test suite for calculate_topic_relevance function."""

    def test_exact_match_high_score(self):
        """Exact topic match should give high score."""
        score = calculate_topic_relevance(
            "Machine Learning for Computer Vision",
            ["Machine Learning"]
        )
        assert score >= 0.8

    def test_partial_match_medium_score(self):
        """Partial match should give medium score."""
        score = calculate_topic_relevance(
            "Deep Learning Approaches",
            ["Machine Learning"]
        )
        assert 0.3 < score < 0.9

    def test_no_match_low_score(self):
        """No match should give low score."""
        score = calculate_topic_relevance(
            "Ocean Temperature Analysis",
            ["Machine Learning", "NLP"]
        )
        assert score < 0.3

    def test_multiple_topics_boost_score(self):
        """Multiple matching topics should boost score."""
        single_score = calculate_topic_relevance(
            "Machine Learning",
            ["Machine Learning"]
        )
        multi_score = calculate_topic_relevance(
            "Machine Learning and NLP",
            ["Machine Learning", "NLP"]
        )
        assert multi_score >= single_score

    def test_score_bounded_0_to_1(self):
        """Score should always be between 0 and 1."""
        score = calculate_topic_relevance(
            "Machine Learning NLP AI Deep Learning",
            ["Machine Learning", "NLP", "AI", "Deep Learning"]
        )
        assert 0 <= score <= 1
