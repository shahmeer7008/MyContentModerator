# File: agents/decision_maker.py
"""Decision Maker Agent - Makes final moderation decision."""

import json
from datetime import datetime
from state import ModerationState
from llm_client import LLMClient
from moderator import Config

class DecisionMakerAgent:
    """Makes final moderation decision based on all agent inputs."""
    
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client
    
    def analyze(self, state: ModerationState) -> ModerationState:
        """Make final moderation decision."""
        
        # Prepare comprehensive summary for decision making
        agents_summary = {
            "initial_scan": state.get('initial_scan', {}),
            "toxicity_analysis": state.get('toxicity_analysis', {}),
            "spam_analysis": state.get('spam_analysis', {}),
            "pii_analysis": state.get('pii_analysis', {}),
            "context_analysis": state.get('context_analysis', {}),
            "flags": state.get('flags', []),
            "severity_scores": state.get('severity_scores', {})
        }
        
        prompt = f"""You are the Decision Maker Agent. Review all agent reports and make a final moderation decision.

Content: {state['content']}

=== AGENT REPORTS ===
{json.dumps(agents_summary, indent=2)}

=== YOUR DECISION CRITERIA ===
**APPROVE**: Safe content, low risk, no significant violations
- False positives identified by context analyzer
- Educational or journalistic content
- No serious violations detected

**REVIEW**: Borderline content, needs human judgment
- Moderate severity scores
- Context unclear or ambiguous
- Multiple minor violations
- Cultural sensitivity concerns
- Context analyzer suggests human review

**REJECT**: Clear violations, high risk, immediate action needed
- High toxicity or hate speech
- Serious threats or violence
- Dangerous scams or phishing
- Severe privacy violations
- Multiple high-severity violations

Make a final decision in JSON:
{{
    "decision": "APPROVE/REVIEW/REJECT",
    "confidence": 0.0-1.0,
    "primary_reason": "single most important reason for this decision",
    "risk_level": "low/medium/high/critical",
    "violated_categories": ["list of policy categories violated"],
    "recommended_actions": ["specific actions to take"],
    "explanation": "comprehensive explanation for human reviewers",
    "auto_actionable": true/false,
    "escalation_needed": true/false,
    "time_sensitivity": "immediate/normal/low"
}}

Be fair but firm. Protect users while avoiding censorship of legitimate content."""

        try:
            response = self.llm.invoke(prompt)
            decision = json.loads(response)
        except Exception as e:
            decision = {
                "decision": Config.REVIEW,
                "confidence": 0.5,
                "primary_reason": "Error in decision making process",
                "risk_level": Config.RISK_MEDIUM,
                "violated_categories": [],
                "recommended_actions": ["Manual review required due to system error"],
                "explanation": f"System encountered an error: {str(e)}",
                "auto_actionable": False,
                "escalation_needed": True,
                "time_sensitivity": "normal"
            }
        
        return {
            **state,
            "final_decision": decision,
            "agents_used": ["Decision Maker"],
            "agent_reports": [{
                "agent": "Decision Maker",
                "timestamp": datetime.now().isoformat(),
                "findings": decision
            }]
        }