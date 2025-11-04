# File: agents/context_analyzer.py
"""Context Analyzer Agent - Understands nuance and reduces false positives."""

import json
from datetime import datetime
from state import ModerationState
from llm_client import LLMClient

class ContextAnalyzerAgent:
    """Analyzes context, intent, and nuance to reduce false positives."""
    
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client
    
    def analyze(self, state: ModerationState) -> ModerationState:
        """Perform context analysis."""
        
        prompt = f"""You are a Context Analyzer Agent. Your role is to understand nuance and context.

Content:
{state['content']}

Previous findings:
- Initial scan: {state['initial_scan']}
- Toxicity analysis: {state.get('toxicity_analysis', 'Not analyzed')}
- Spam analysis: {state.get('spam_analysis', 'Not analyzed')}
- PII analysis: {state.get('pii_analysis', 'Not analyzed')}
- Flags raised: {state.get('flags', [])}

Analyze for:
- Intent (malicious vs educational vs satirical vs neutral)
- Cultural context and idioms
- Sarcasm, irony, or humor
- Self-references that aren't harmful
- Educational, journalistic, or academic content
- Quotes or discussions about problematic content (vs endorsing it)
- False positive likelihood
- Historical or literary references

Provide JSON analysis:
{{
    "likely_intent": "malicious/educational/satirical/journalistic/neutral/unclear",
    "is_false_positive": true/false,
    "false_positive_likelihood": 0.0-1.0,
    "context_explanation": "detailed explanation of context",
    "mitigating_factors": ["factors that reduce severity"],
    "aggravating_factors": ["factors that increase severity"],
    "cultural_considerations": "any cultural context to consider",
    "recommended_override": "none/reduce_severity/increase_severity",
    "human_review_needed": true/false,
    "confidence": 0.0-1.0
}}

Your job is to catch false positives and understand nuance."""

        try:
            response = self.llm.invoke(prompt)
            analysis = json.loads(response)
        except Exception as e:
            analysis = {
                "likely_intent": "neutral",
                "is_false_positive": False,
                "false_positive_likelihood": 0.5,
                "context_explanation": "Unable to determine context",
                "mitigating_factors": [],
                "aggravating_factors": [],
                "cultural_considerations": "None identified",
                "recommended_override": "none",
                "human_review_needed": True,
                "confidence": 0.5
            }
        
        flags = []
        if analysis.get("is_false_positive"):
            flags.append("likely_false_positive")
        if analysis.get("human_review_needed"):
            flags.append("needs_human_review")
        
        return {
            **state,
            "context_analysis": analysis,
            "flags": flags,
            "agents_used": ["Context Analyzer"],
            "agent_reports": [{
                "agent": "Context Analyzer",
                "timestamp": datetime.now().isoformat(),
                "findings": analysis
            }]
        }