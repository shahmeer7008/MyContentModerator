# File: config.py
"""Configuration settings for the moderation system."""

class Config:
    """System configuration."""
    
    # Groq API settings - Available models:
    # - llama-3.1-70b-versatile (best quality)
    # - llama-3.1-8b-instant (fastest)
    # - mixtral-8x7b-32768 (good balance)
    GROQ_MODEL = "llama-3.1-8b-instant"
    TEMPERATURE = 0
    
    # Moderation thresholds
    HIGH_TOXICITY_THRESHOLD = 0.7
    MEDIUM_TOXICITY_THRESHOLD = 0.4
    HIGH_CONFIDENCE_THRESHOLD = 0.8
    
    # Decision types
    APPROVE = "APPROVE"
    REVIEW = "REVIEW"
    REJECT = "REJECT"
    
    # Risk levels
    RISK_LOW = "low"
    RISK_MEDIUM = "medium"
    RISK_HIGH = "high"
    RISK_CRITICAL = "critical"