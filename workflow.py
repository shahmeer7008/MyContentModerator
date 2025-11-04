# File: workflow.py
"""LangGraph workflow for multi-agent moderation."""

from langgraph.graph import StateGraph, END
from state import ModerationState
from llm_client import LLMClient
from agents.initial_scanner import InitialScannerAgent
from agents.toxicity_analyzer import ToxicityAnalyzerAgent
from agents.spam_analyzer import SpamAnalyzerAgent
from agents.pii_analyzer import PIIAnalyzerAgent
from agents.context_analyzer import ContextAnalyzerAgent
from agents.decision_maker import DecisionMakerAgent
from moderator import Config
import time

class ModerationWorkflow:
    """Manages the multi-agent moderation workflow."""
    
    def __init__(self, api_key: str):
        """Initialize workflow with agents."""
        self.llm_client = LLMClient(api_key)
        
        # Initialize all agents
        self.initial_scanner = InitialScannerAgent(self.llm_client)
        self.toxicity_analyzer = ToxicityAnalyzerAgent(self.llm_client)
        self.spam_analyzer = SpamAnalyzerAgent(self.llm_client)
        self.pii_analyzer = PIIAnalyzerAgent(self.llm_client)
        self.context_analyzer = ContextAnalyzerAgent(self.llm_client)
        self.decision_maker = DecisionMakerAgent(self.llm_client)
        
        # Build the graph
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow."""
        
        workflow = StateGraph(ModerationState)
        
        # Add all agent nodes
        workflow.add_node("initial_scanner", self.initial_scanner.analyze)
        workflow.add_node("toxicity_analyzer", self.toxicity_analyzer.analyze)
        workflow.add_node("spam_analyzer", self.spam_analyzer.analyze)
        workflow.add_node("pii_analyzer", self.pii_analyzer.analyze)
        workflow.add_node("context_analyzer", self.context_analyzer.analyze)
        workflow.add_node("decision_maker", self.decision_maker.analyze)
        
        # Set entry point
        workflow.set_entry_point("initial_scanner")
        
        # Routing logic after initial scan
        def route_after_initial_scan(state: ModerationState) -> str:
            """Route to appropriate specialized agents based on initial scan."""
            initial = state["initial_scan"]
            risk_level = initial.get("initial_risk_level", "medium")
            recommended = initial.get("recommended_agents", [])
            
            # Low risk content can skip to decision
            if risk_level == "low" and not recommended:
                return "decision_maker"
            
            # Route to first recommended agent or toxicity by default
            if "toxicity_analyzer" in recommended:
                return "toxicity_analyzer"
            elif "spam_analyzer" in recommended:
                return "spam_analyzer"
            elif "pii_analyzer" in recommended:
                return "pii_analyzer"
            else:
                return "toxicity_analyzer"
        
        # Add conditional routing from initial scanner
        workflow.add_conditional_edges(
            "initial_scanner",
            route_after_initial_scan,
            {
                "toxicity_analyzer": "toxicity_analyzer",
                "spam_analyzer": "spam_analyzer",
                "pii_analyzer": "pii_analyzer",
                "decision_maker": "decision_maker"
            }
        )
        
        # Routing after toxicity analysis
        def route_after_toxicity(state: ModerationState) -> str:
            """Route after toxicity analysis."""
            recommended = state["initial_scan"].get("recommended_agents", [])
            
            if "spam_analyzer" in recommended and "spam_analysis" not in state:
                return "spam_analyzer"
            elif "pii_analyzer" in recommended and "pii_analysis" not in state:
                return "pii_analyzer"
            else:
                return "context_analyzer"
        
        workflow.add_conditional_edges(
            "toxicity_analyzer",
            route_after_toxicity,
            {
                "spam_analyzer": "spam_analyzer",
                "pii_analyzer": "pii_analyzer",
                "context_analyzer": "context_analyzer"
            }
        )
        
        # Routing after spam analysis
        def route_after_spam(state: ModerationState) -> str:
            """Route after spam analysis."""
            recommended = state["initial_scan"].get("recommended_agents", [])
            
            if "pii_analyzer" in recommended and "pii_analysis" not in state:
                return "pii_analyzer"
            elif "toxicity_analysis" not in state:
                return "toxicity_analyzer"
            else:
                return "context_analyzer"
        
        workflow.add_conditional_edges(
            "spam_analyzer",
            route_after_spam,
            {
                "pii_analyzer": "pii_analyzer",
                "toxicity_analyzer": "toxicity_analyzer",
                "context_analyzer": "context_analyzer"
            }
        )
        
        # Routing after PII analysis
        def route_after_pii(state: ModerationState) -> str:
            """Route after PII analysis."""
            if "toxicity_analysis" not in state:
                return "toxicity_analyzer"
            elif "spam_analysis" not in state:
                return "spam_analyzer"
            else:
                return "context_analyzer"
        
        workflow.add_conditional_edges(
            "pii_analyzer",
            route_after_pii,
            {
                "toxicity_analyzer": "toxicity_analyzer",
                "spam_analyzer": "spam_analyzer",
                "context_analyzer": "context_analyzer"
            }
        )
        
        # Context analyzer always goes to decision maker
        workflow.add_edge("context_analyzer", "decision_maker")
        
        # Decision maker is the end
        workflow.add_edge("decision_maker", END)
        
        return workflow.compile()
    
    def moderate(self, content: str) -> ModerationState:
        """Run content through the moderation workflow."""
        
        start_time = time.time()
        
        # Initialize state
        initial_state = {
            "content": content,
            "initial_scan": {},
            "toxicity_analysis": {},
            "context_analysis": {},
            "spam_analysis": {},
            "pii_analysis": {},
            "final_decision": {},
            "flags": [],
            "severity_scores": {},
            "agent_reports": [],
            "processing_time": 0.0,
            "agents_used": []
        }
        
        # Run the workflow
        result = self.graph.invoke(initial_state)
        
        # Add processing time
        result["processing_time"] = time.time() - start_time
        
        return result