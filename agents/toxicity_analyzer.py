# File: agents/toxicity_analyzer.py
"""Toxicity Analyzer Agent - Deep analysis of harmful content."""

import json
from datetime import datetime
from state import ModerationState
from llm_client import LLMClient
from moderator import Config

class ToxicityAnalyzerAgent:
    """Analyzes content for toxic, harmful, or hateful language."""
    
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client
    
    def analyze(self, state: ModerationState) -> ModerationState:
        """Perform toxicity analysis."""
        
        prompt = f"""You are a Toxicity Analyzer Agent specializing in detecting harmful language.

Analyze this content for:
- Hate speech and discrimination (racism, sexism, homophobia, etc.)
- Harassment, bullying, and personal attacks
- Threats and violence
- Toxic language patterns
- Offensive slurs or derogatory terms
- Dangerous ideologies

Content:
{state['content']}

Initial scan found: {state['initial_scan'].get('obvious_violations', [])}

Provide detailed analysis in JSON:
{{
    "overall_toxicity_score": 0.0-1.0,
    "categories_detected": {{
        "hate_speech": 0.0-1.0,
        "harassment": 0.0-1.0,
        "violence": 0.0-1.0,
        "profanity": 0.0-1.0,
        "identity_attack": 0.0-1.0,
        "threat": 0.0-1.0
    }},
    "specific_violations": ["detailed list of specific issues found"],
    "problematic_phrases": ["exact phrases that are concerning"],
    "target_groups": ["groups being targeted, if any"],
    "severity_explanation": "why this content is or isn't severe",
    "context_matters": true/false,
    "confidence": 0.0-1.0
}}

Be thorough and specific about what makes content toxic."""

        try:
            response = self.llm.invoke(prompt)
            analysis = json.loads(response)
        except Exception as e:
            analysis = {
                "overall_toxicity_score": 0.5,
                "categories_detected": {},
                "specific_violations": [],
                "problematic_phrases": [],
                "target_groups": [],
                "severity_explanation": "Error in analysis",
                "context_matters": False,
                "confidence": 0.5
            }
        
        # Add flags based on toxicity
        flags = []
        if analysis.get("overall_toxicity_score", 0) > Config.HIGH_TOXICITY_THRESHOLD:
            flags.append("high_toxicity")
        if analysis.get("overall_toxicity_score", 0) > Config.MEDIUM_TOXICITY_THRESHOLD:
            flags.append("moderate_toxicity")
        
        severity_scores = analysis.get("categories_detected", {})
        
        return {
            **state,
            "toxicity_analysis": analysis,
            "flags": flags,
            "severity_scores": {**state.get("severity_scores", {}), **severity_scores},
            "agents_used": ["Toxicity Analyzer"],
            "agent_reports": [{
                "agent": "Toxicity Analyzer",
                "timestamp": datetime.now().isoformat(),
                "findings": analysis
            }]
        }