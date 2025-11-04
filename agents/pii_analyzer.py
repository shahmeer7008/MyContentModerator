# File: agents/pii_analyzer.py
"""PII Analyzer Agent - Detects personal identifiable information."""

import json
from datetime import datetime
from state import ModerationState
from llm_client import LLMClient

class PIIAnalyzerAgent:
    """Analyzes content for personal identifiable information leaks."""
    
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client
    
    def analyze(self, state: ModerationState) -> ModerationState:
        """Perform PII analysis."""
        
        prompt = f"""You are a PII Analyzer Agent specializing in detecting personal information.

Analyze this content for:
- Email addresses
- Phone numbers
- Physical addresses
- Social security numbers or ID numbers
- Credit card information
- Personal names with identifying details
- Account credentials
- Medical information
- Financial information

Content:
{state['content']}

Provide analysis in JSON:
{{
    "pii_detected": true/false,
    "pii_types_found": ["list of PII types detected"],
    "pii_count": number of PII instances,
    "severity": "low/medium/high/critical",
    "redaction_needed": true/false,
    "privacy_risk": 0.0-1.0,
    "specific_findings": ["general descriptions without revealing actual PII"],
    "recommendation": "what should be done about detected PII",
    "confidence": 0.0-1.0
}}

IMPORTANT: In your response, describe what types of PII were found but DO NOT reproduce the actual PII data."""

        try:
            response = self.llm.invoke(prompt)
            analysis = json.loads(response)
        except Exception as e:
            analysis = {
                "pii_detected": False,
                "pii_types_found": [],
                "pii_count": 0,
                "severity": "low",
                "redaction_needed": False,
                "privacy_risk": 0.0,
                "specific_findings": [],
                "recommendation": "No action needed",
                "confidence": 0.5
            }
        
        flags = []
        if analysis.get("pii_detected"):
            flags.append("pii_detected")
        if analysis.get("privacy_risk", 0) > 0.7:
            flags.append("high_privacy_risk")
        
        return {
            **state,
            "pii_analysis": analysis,
            "flags": flags,
            "agents_used": ["PII Analyzer"],
            "agent_reports": [{
                "agent": "PII Analyzer",
                "timestamp": datetime.now().isoformat(),
                "findings": analysis
            }]
        }