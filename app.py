# File: app.py
"""Gradio interface for the multi-agent moderation system."""

import gradio as gr
from workflow import ModerationWorkflow
from moderator import Config
import json

class ModerationApp:
    """Gradio application wrapper."""
    
    def __init__(self):
        self.workflow = None
        self.moderation_history = []
        self.api_configured = False
    
    def configure_api(self, api_key: str) -> tuple:
        """Configure the API key."""
        if not api_key.strip():
            return "⚠️ Please enter a valid API key", gr.update(visible=False)
        
        try:
            # Test the API key
            self.workflow = ModerationWorkflow(api_key)
            self.api_configured = True
            return "✅ API configured successfully!", gr.update(visible=True)
        except Exception as e:
            return f"❌ Configuration failed: {str(e)}", gr.update(visible=False)
    
    def moderate_content(self, content: str) -> tuple:
        """Run content through moderation workflow."""
        
        if not content.strip():
            return "⚠️ Please enter content to moderate", ""
        
        if not self.api_configured:
            return "⚠️ Please configure your API key first", ""
        
        try:
            # Run moderation
            result = self.workflow.moderate(content)
            
            # Add to history
            self.moderation_history.append(result)
            
            # Format outputs
            decision_output = self._format_decision(result)
            details_output = self._format_details(result)
            
            return decision_output, details_output
            
        except Exception as e:
            error_msg = f"❌ Error during moderation: {str(e)}"
            return error_msg, ""
    
    def _format_decision(self, result: dict) -> str:
        """Format the final decision - clean and elegant."""
        decision = result.get("final_decision", {})
        
        decision_emoji = {
            "APPROVE": "✅",
            "REVIEW": "⚠️",
            "REJECT": "❌"
        }
        
        risk_emoji = {
            "low": "🟢",
            "medium": "🟡",
            "high": "🟠",
            "critical": "🔴"
        }
        
        decision_type = decision.get("decision", "UNKNOWN")
        risk_level = decision.get("risk_level", "unknown")
        
        output = f"""
<div style="text-align: center; padding: 20px;">
    <h2 style="font-size: 2.5em; margin: 10px 0;">{decision_emoji.get(decision_type, '❓')}</h2>
    <h3 style="margin: 10px 0; color: #333;">{decision_type}</h3>
    <p style="color: #666; font-size: 0.9em;">
        {risk_emoji.get(risk_level, '⚪')} {risk_level.upper()} RISK
        <span style="margin: 0 10px;">•</span>
        {decision.get('confidence', 0):.0%} Confidence
        <span style="margin: 0 10px;">•</span>
        {result.get('processing_time', 0):.1f}s
    </p>
</div>

---

### 📋 Analysis

**Reason:** {decision.get('primary_reason', 'No reason provided')}

{decision.get('explanation', '')}
"""
        
        # Add violated categories if any
        if decision.get('violated_categories'):
            output += f"\n\n**⚠️ Violations:** {', '.join(decision.get('violated_categories'))}"
        
        # Add recommended actions
        if decision.get('recommended_actions'):
            output += "\n\n**✅ Recommended Actions:**\n"
            for action in decision.get('recommended_actions', []):
                output += f"- {action}\n"
        
        return output
    
    def _format_details(self, result: dict) -> str:
        """Format detailed analysis - elegant expandable sections."""
        output = ""
        
        # Severity scores
        severity_scores = result.get("severity_scores", {})
        if severity_scores:
            output += "### 📊 Risk Categories\n\n"
            for category, score in sorted(severity_scores.items(), key=lambda x: x[1], reverse=True):
                bar_length = int(score * 30)
                bar = "█" * bar_length + "░" * (30 - bar_length)
                
                if score > 0.7:
                    emoji = "🔴"
                elif score > 0.4:
                    emoji = "🟡"
                else:
                    emoji = "🟢"
                
                output += f"{emoji} **{category.replace('_', ' ').title()}**  \n"
                output += f"`{bar}` {score:.0%}\n\n"
        
        # Flags
        flags = result.get("flags", [])
        if flags:
            output += "\n### 🚩 Detection Flags\n\n"
            for flag in set(flags):
                output += f"• {flag.replace('_', ' ').title()}\n"
        
        # Processing stats
        agents = result.get("agents_used", [])
        output += f"\n\n---\n\n"
        output += f"**Agents Used:** {', '.join(set(agents))}\n\n"
        output += f"**Processing Time:** {result.get('processing_time', 0):.2f}s"
        
        # Session stats if available
        if len(self.moderation_history) > 1:
            decisions = [h['final_decision'].get('decision') for h in self.moderation_history]
            output += f"\n\n**Session:** {decisions.count('APPROVE')} Approved • "
            output += f"{decisions.count('REVIEW')} Review • "
            output += f"{decisions.count('REJECT')} Rejected"
        
        return output

def create_gradio_interface():
    """Create an elegant Gradio interface."""
    
    app = ModerationApp()
    
    # Custom CSS for elegant design
    custom_css = """
    .gradio-container {
        max-width: 1400px !important;
    }
    .main-title {
        text-align: center;
        font-size: 2.5em;
        font-weight: 600;
        margin-bottom: 10px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 1.1em;
        margin-bottom: 30px;
    }
    .config-success {
        padding: 10px;
        border-radius: 8px;
        background: #d4edda;
        color: #155724;
        margin: 10px 0;
    }
    """
    
    with gr.Blocks(title="Content Moderation System", theme=gr.themes.Soft(), css=custom_css) as interface:
        
        # Main Title - Centered
        gr.HTML("""
            <div class="main-title">🛡️ Content Moderation System</div>
            <div class="subtitle">AI-powered content safety analysis</div>
        """)
        
        with gr.Row():
            # Sidebar for Configuration
            with gr.Column(scale=1):
                gr.Markdown("### ⚙️ Configuration")
                
                api_key_input = gr.Textbox(
                    label="Groq API Key",
                    type="password",
                    placeholder="gsk_...",
                    info="Enter your API key to begin"
                )
                
                configure_btn = gr.Button(
                    "Configure API",
                    variant="primary",
                    size="sm"
                )
                
                config_status = gr.Markdown("")
                
                gr.Markdown("""
                ---
                
                ### 📚 Need an API Key?
                
                1. Visit [console.groq.com](https://console.groq.com)
                2. Sign up for free
                3. Generate API key
                4. Paste above
                
                ---
                
                ### 📊 Quick Stats
                """)
                
                stats_display = gr.Markdown("*No moderations yet*")
            
            # Main Content Area
            with gr.Column(scale=3):
                with gr.Row():
                    # Input Area
                    with gr.Column(scale=1):
                        gr.Markdown("### 📝 Content to Moderate")
                        content_input = gr.Textbox(
                            label="",
                            placeholder="Enter text, comments, or posts to analyze...",
                            lines=15,
                            show_label=False
                        )
                        
                        moderate_btn = gr.Button(
                            "🔍 Analyze Content",
                            variant="primary",
                            size="lg",
                            visible=False  # Hidden until API configured
                        )
                    
                    # Results Area
                    with gr.Column(scale=1):
                        gr.Markdown("### 📊 Moderation Result")
                        decision_output = gr.Markdown(
                            value="*Results will appear here*",
                            show_label=False
                        )
                
                # Expandable Details Section
                with gr.Accordion("📋 Detailed Analysis", open=False):
                    details_output = gr.Markdown()
        
        # Event Handlers
        def configure_and_update(api_key):
            status, btn_update = app.configure_api(api_key)
            stats = f"**Status:** Ready  \n**Model:** {Config.GROQ_MODEL}"
            return status, btn_update, stats
        
        configure_btn.click(
            configure_and_update,
            inputs=[api_key_input],
            outputs=[config_status, moderate_btn, stats_display]
        )
        
        def moderate_and_update(content):
            decision, details = app.moderate_content(content)
            # Update stats
            if app.moderation_history:
                total = len(app.moderation_history)
                decisions = [h['final_decision'].get('decision') for h in app.moderation_history]
                stats = f"""**Total:** {total} moderations  
**Approved:** {decisions.count('APPROVE')}  
**Review:** {decisions.count('REVIEW')}  
**Rejected:** {decisions.count('REJECT')}"""
                return decision, details, stats
            return decision, details, gr.update()
        
        moderate_btn.click(
            moderate_and_update,
            inputs=[content_input],
            outputs=[decision_output, details_output, stats_display]
        )
        
        # Footer
        gr.Markdown("""
        <div style="text-align: center; margin-top: 40px; padding: 20px; color: #999; font-size: 0.9em;">
            <p>Powered by LangGraph • Groq AI • Multi-Agent Architecture</p>
        </div>
        """)
    
    return interface

if __name__ == "__main__":
    app = create_gradio_interface()
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        ssr_mode=False,
        show_error=True
    )