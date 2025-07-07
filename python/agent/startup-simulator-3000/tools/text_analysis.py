from typing import Dict, Any
from agent_framework.tools.base import BaseTool
from agent_framework.models import ToolMetadata

class TextAnalyzerTool(BaseTool):
    """Tool for analyzing text complexity"""

    @classmethod
    def get_metadata(cls) -> ToolMetadata:
        """Get tool metadata"""
        return ToolMetadata(
            name="text_analyzer",
            description="Analyzes text for complexity and readability",
            tags=["text", "analysis", "complexity"],
            input_schema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text to analyze"
                    }
                },
                "required": ["text"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "complexity_score": {"type": "number"},
                    "readability_level": {"type": "string"},
                    "analysis": {"type": "string"}
                }
            }
        )

    async def execute(self, text: str) -> Dict[str, Any]:
        """Analyze text complexity"""
        # Simple implementation - in real world would use NLP
        word_count = len(text.split())
        avg_word_length = sum(len(word) for word in text.split()) / word_count if word_count > 0 else 0
        
        # Calculate complexity score (0-10)
        complexity_score = min(10, (avg_word_length - 3) * 2)
        
        # Determine readability level
        if complexity_score < 4:
            level = "Easy"
        elif complexity_score < 7:
            level = "Moderate"
        else:
            level = "Complex"
            
        return {
            "complexity_score": complexity_score,
            "readability_level": level,
            "analysis": f"Text contains {word_count} words with average length of {avg_word_length:.1f} characters."
        } 