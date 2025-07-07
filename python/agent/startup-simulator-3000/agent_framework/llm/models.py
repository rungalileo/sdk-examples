from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class LLMMessage(BaseModel):
    """Message format for LLM interactions"""
    role: str
    content: str
    name: Optional[str] = None

class LLMResponse(BaseModel):
    """Structured response from LLM"""
    content: str
    raw_response: Dict[str, Any] = Field(default_factory=dict)
    finish_reason: Optional[str] = None
    usage: Optional[Dict[str, int]] = None

class LLMConfig(BaseModel):
    """Configuration for LLM provider"""
    model: str
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    stop: Optional[List[str]] = None
    custom_settings: Dict[str, Any] = Field(default_factory=dict)

class ToolSelectionOutput(BaseModel):
    """Output from tool selection"""
    selected_tools: List[str] = Field(
        description="Names of the selected tools in order of execution"
    )
    confidence: float = Field(
        description="Confidence score for the tool selection (0-1)",
        ge=0.0,
        le=1.0
    )
    reasoning_steps: List[str] = Field(
        description="List of reasoning steps that led to the tool selection"
    )

    @classmethod
    def model_json_schema(cls) -> Dict[str, Any]:
        """Get JSON schema with example"""
        schema = super().model_json_schema()
        schema["examples"] = [{
            "selected_tools": ["text_analyzer", "sentiment_analyzer"],
            "confidence": 0.9,
            "reasoning_steps": [
                "Task involves understanding text complexity and sentiment",
                "Text analyzer provides detailed analysis capabilities",
                "Sentiment analyzer provides sentiment analysis capabilities",
                "Other tools don't provide required capabilities"
            ]
        }]
        return schema