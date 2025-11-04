# File: agents/spam_analyzer.py
"""Spam Analyzer Agent - Detects spam, scams, and promotional content."""

import json
from datetime import datetime
from state import ModerationState
from llm_client import LLMClient

class SpamAnalyzerAgent:
    """Analyzes content for spam, scams, and unwanted promotional content."""
    
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client
    
    def analyze(self, state: ModerationState) -> ModerationState:
        """Perform spam analysis."""
        
        prompt = f"""You are a Spam Analyzer Agent specializing in detecting spam and scams.

Analyze this content for:
- Spam patterns (repetitive, promotional)
- Scams and phishing attempts
- Misleading offers or clickbait
- Excessive links or promotional content
- Bot-like behavior patterns
- Pyramid schemes or MLM content

Content:
{state['content']}

Provide analysis in JSON:
{{
    "spam_score": 0.0-1.0,
    "spam_indicators": {{
        "repetitive_content": 0.0-1.0,
        "excessive_links": 0.0-1.0,
        "promotional": 0.0-1.0,
        "scam_likelihood": 0.0-1.0,
        "bot_like": 0.0-1.0
    }},
    "detected_patterns": ["list of spam patterns found"],
    "suspicious_elements": ["URLs, phone numbers, or other suspicious elements"],
    "is_likely_spam": true/false,
    "commercial_intent": true/false,
    "confidence": 0.0-1.0
}}"""

        try:
            response = self.llm.invoke(prompt)
            analysis = json.loads(response)
        except Exception as e:
            analysis = {
                "spam_score": 0.0,
                "spam_indicators": {},
                "detected_patterns": [],
                "suspicious_elements": [],
                "is_likely_spam": False,
                "commercial_intent": False,
                "confidence": 0.5
            }
        
        flags = []
        if analysis.get("spam_score", 0) > 0.7:
            flags.append("high_spam")
        if analysis.get("is_likely_spam"):
            flags.append("spam_detected")
        
        return {
            **state,
            "spam_analysis": analysis,
            "flags": flags,
            "agents_used": ["Spam Analyzer"],
            "agent_reports": [{
                "agent": "Spam Analyzer",
                "timestamp": datetime.now().isoformat(),
                "findings": analysis
            }]
        }