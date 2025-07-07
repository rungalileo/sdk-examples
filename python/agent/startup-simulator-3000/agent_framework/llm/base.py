from abc import ABC, abstractmethod
from typing import List, Optional

from .models import LLMMessage, LLMResponse, LLMConfig

class LLMProvider(ABC):
    """Base class for LLM providers"""
    
    def __init__(self, config: LLMConfig):
        self.config = config

    @abstractmethod
    async def generate(
        self,
        messages: List[LLMMessage],
        config: Optional[LLMConfig] = None
    ) -> LLMResponse:
        """Generate a response from the LLM"""
        pass

    @abstractmethod
    async def generate_stream(
        self,
        messages: List[LLMMessage],
        config: Optional[LLMConfig] = None
    ):
        """Generate a streaming response from the LLM"""
        pass 