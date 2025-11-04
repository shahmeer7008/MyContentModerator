# File: agents/initial_scanner.py
"""Initial Scanner Agent - Quick triage and categorization."""

import json
from datetime import datetime
from state import ModerationState
from llm_client import LLMClient

class InitialScannerAgent:
    """Performs quick initial scan to categorize content."""
    
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client
    
    def analyze(self, state: ModerationState) -> ModerationState:
        """Perform initial scan of content."""
        
        prompt = f"""You are an Initial Scanner Agent in a content moderation system.

Your task: Perform a quick scan to identify content type and obvious violations.

Content to analyze:
{state['content']}

Provide analysis in JSON format:
{{
    "content_type": "text/social_post/comment/article/code/etc",
    "language": "detected language",
    "length_category": "short/medium/long",
    "obvious_violations": ["list of immediately apparent violations"],
    "suspicious_patterns": ["list of concerning patterns"],
    "requires_deep_scan": true/false,
    "initial_risk_level": "low/medium/high",
    "recommended_agents": ["list of which agents should analyze this"]
}}

Be quick and focus on immediate red flags. Recommend agents from:
- toxicity_analyzer (for hate speech, harassment, violence)
- spam_analyzer (for spam, scams, promotions)
- pii_analyzer (for personal information leaks)"""

        try:
            response = self.llm.invoke(prompt)
            analysis = json.loads(response)
        except Exception as e:
            analysis = {
                "content_type": "unknown",
                "language": "unknown",
                "length_category": "unknown",
                "obvious_violations": [],
                "suspicious_patterns": [],
                "requires_deep_scan": True,
                "initial_risk_level": "medium",
                "recommended_agents": ["toxicity_analyzer"]
            }
        
        return {
            **state,
            "initial_scan": analysis,
            "agents_used": ["Initial Scanner"],
            "agent_reports": [{
                "agent": "Initial Scanner",
                "timestamp": datetime.now().isoformat(),
                "findings": analysis
            }]
        }