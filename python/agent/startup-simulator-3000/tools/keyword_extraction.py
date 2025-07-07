from typing import Dict, Any, List
from agent_framework.tools.base import BaseTool
from agent_framework.models import ToolMetadata

class KeywordExtractorTool(BaseTool):
    """Tool for extracting keywords from text"""

    @classmethod
    def get_metadata(cls) -> ToolMetadata:
        """Get tool metadata"""
        return ToolMetadata(
            name="keyword_extractor",
            description="Extracts important keywords and phrases from text",
            tags=["text", "keywords", "extraction"],
            input_schema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Text to extract keywords from"
                    }
                },
                "required": ["text"]
            },
            output_schema={
                "type": "object",
                "properties": {
                    "keywords": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "importance_scores": {
                        "type": "object",
                        "additionalProperties": {"type": "number"}
                    }
                }
            }
        )

    async def execute(self, text: str) -> Dict[str, Any]:
        """Extract keywords from text"""
        # Simple implementation - in real world would use NLP
        words = text.lower().split()
        word_freq = {}
        
        # Count word frequencies
        for word in words:
            if len(word) > 3:  # Only consider words longer than 3 chars
                word_freq[word] = word_freq.get(word, 0) + 1
                
        # Get top keywords by frequency
        keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Calculate importance scores (normalized frequencies)
        max_freq = max(freq for _, freq in keywords) if keywords else 1
        importance_scores = {
            word: freq / max_freq 
            for word, freq in keywords
        }
            
        return {
            "keywords": [word for word, _ in keywords],
            "importance_scores": importance_scores
        } 