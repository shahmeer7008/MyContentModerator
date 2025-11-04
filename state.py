# File: state.py
"""State definitions for the moderation workflow."""

from typing import TypedDict, Annotated, List, Dict, Any
import operator

class ModerationState(TypedDict):
    """State object passed between agents in the workflow."""
    
    # Input
    content: str
    
    # Agent analyses
    initial_scan: Dict[str, Any]
    toxicity_analysis: Dict[str, Any]
    context_analysis: Dict[str, Any]
    spam_analysis: Dict[str, Any]
    pii_analysis: Dict[str, Any]
    final_decision: Dict[str, Any]
    
    # Accumulated data
    flags: Annotated[List[str], operator.add]
    severity_scores: Dict[str, float]
    agent_reports: Annotated[List[Dict], operator.add]
    
    # Metadata
    processing_time: float
    agents_used: Annotated[List[str], operator.add]