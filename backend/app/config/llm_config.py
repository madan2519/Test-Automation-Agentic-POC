"""
Global LLM Model Configuration
Central place to configure which LLM model to use across all agents.
"""

# LLM Model Configuration
LLM_MODEL = "gpt-4"  # Options: "gpt-3.5-turbo", "gpt-4", "gpt-4-turbo", "claude-3-opus", etc.
LLM_TEMPERATURE = 0.1  # Lower = more deterministic, Higher = more creative
LLM_MAX_TOKENS = 4000  # Maximum tokens for responses

# OpenAI Configuration
OPENAI_MODEL = LLM_MODEL
OPENAI_TEMPERATURE = LLM_TEMPERATURE
OPENAI_MAX_TOKENS = LLM_MAX_TOKENS

# Agent-specific configurations (can override global settings if needed)
ORCHESTRATOR_MODEL = LLM_MODEL
ORCHESTRATOR_TEMPERATURE = LLM_TEMPERATURE

TEST_PLAN_MODEL = LLM_MODEL
TEST_PLAN_TEMPERATURE = LLM_TEMPERATURE

RETRY_AGENT_MODEL = LLM_MODEL
RETRY_AGENT_TEMPERATURE = LLM_TEMPERATURE

STRUCTURING_AGENT_MODEL = LLM_MODEL
STRUCTURING_AGENT_TEMPERATURE = LLM_TEMPERATURE

# Export for easy access
__all__ = [
    'LLM_MODEL',
    'LLM_TEMPERATURE', 
    'LLM_MAX_TOKENS',
    'OPENAI_MODEL',
    'OPENAI_TEMPERATURE',
    'OPENAI_MAX_TOKENS',
    'ORCHESTRATOR_MODEL',
    'ORCHESTRATOR_TEMPERATURE',
    'TEST_PLAN_MODEL',
    'TEST_PLAN_TEMPERATURE',
    'RETRY_AGENT_MODEL',
    'RETRY_AGENT_TEMPERATURE',
    'STRUCTURING_AGENT_MODEL',
    'STRUCTURING_AGENT_TEMPERATURE'
]
