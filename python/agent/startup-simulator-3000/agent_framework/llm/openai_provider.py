from typing import Any, Dict, List, Optional, AsyncGenerator, Type, TypeVar
from galileo.openai import openai  # Use Galileo's OpenAI wrapper
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import asyncio

from .base import LLMProvider
from .models import LLMMessage, LLMResponse, LLMConfig

T = TypeVar("T", bound=BaseModel)


class OpenAIProvider(LLMProvider):
    """OpenAI implementation of LLM provider with support for both regular and project-based keys"""

    def __init__(self, config: LLMConfig, organization: Optional[str] = None):
        super().__init__(config)

        # Load environment variables
        load_dotenv()

        # Use provided API key or load from environment
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key must be provided or set in OPENAI_API_KEY environment variable")

        # Check if this is a project-based key
        self.is_project_key = self.api_key.startswith("sk-proj-")

        # Get project ID for project-based keys (for logging purposes)
        self.project_id = None
        if self.is_project_key:
            self.project_id = os.getenv("OPENAI_PROJECT_ID")
            if not self.project_id:
                # Extract project ID from the key if possible
                # Project keys format: sk-proj-{project_id}-{key_id}
                try:
                    parts = self.api_key.split("-")
                    if len(parts) >= 3:
                        self.project_id = parts[2]
                except:
                    pass

        # Initialize the client - project-based keys should work with the standard client
        self.client = openai.AsyncOpenAI(api_key=self.api_key)

        if self.is_project_key:
            print(f"Initialized OpenAI client with project-based key (Project ID: {self.project_id})")
        else:
            print("Initialized OpenAI client with regular API key")

    def _prepare_messages(self, messages: List[LLMMessage]) -> List[Dict[str, Any]]:
        """Convert internal message format to OpenAI format"""
        return [
            {
                "role": msg.role,
                "content": msg.content,
                **({"name": msg.name} if msg.name else {}),
            }
            for msg in messages
        ]

    def _prepare_config(self, config: Optional[LLMConfig] = None) -> Dict[str, Any]:
        """Prepare configuration for OpenAI API"""
        cfg = config or self.config
        return {
            "model": cfg.model,
            "temperature": cfg.temperature,
            "max_tokens": cfg.max_tokens,
            "top_p": cfg.top_p,
            "frequency_penalty": cfg.frequency_penalty,
            "presence_penalty": cfg.presence_penalty,
            "stop": cfg.stop,
            **cfg.custom_settings,
        }

    async def generate(self, messages: List[LLMMessage], config: Optional[LLMConfig] = None) -> LLMResponse:
        """Generate a response using OpenAI"""
        openai_messages = self._prepare_messages(messages)
        api_config = self._prepare_config(config)

        try:
            response = await self.client.chat.completions.create(messages=openai_messages, **api_config)

            choice = response.choices[0]
            usage = response.usage.model_dump() if response.usage else {}
            filtered_usage = {k: v for k, v in usage.items() if isinstance(v, int)}
            return LLMResponse(
                content=choice.message.content,
                raw_response=response.model_dump(),
                finish_reason=choice.finish_reason,
                usage=filtered_usage if filtered_usage else None,
            )
        except Exception as e:
            if "401" in str(e) and self.is_project_key:
                raise ValueError(f"Project-based key authentication failed. Please check your OPENAI_PROJECT_ID and ensure the project exists. Error: {e}")
            raise e

    async def generate_stream(self, messages: List[LLMMessage], config: Optional[LLMConfig] = None) -> AsyncGenerator[LLMResponse, None]:
        """Generate a streaming response using OpenAI"""
        openai_messages = self._prepare_messages(messages)
        api_config = self._prepare_config(config)

        try:
            stream = await self.client.chat.completions.create(messages=openai_messages, stream=True, **api_config)

            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield LLMResponse(
                        content=chunk.choices[0].delta.content,
                        raw_response=chunk.model_dump(),
                        finish_reason=chunk.choices[0].finish_reason,
                    )
        except Exception as e:
            if "401" in str(e) and self.is_project_key:
                raise ValueError(f"Project-based key authentication failed. Please check your OPENAI_PROJECT_ID and ensure the project exists. Error: {e}")
            raise e

    async def generate_structured(
        self,
        messages: List[LLMMessage],
        output_model: Type[T],
        config: Optional[LLMConfig] = None,
    ) -> T:
        """Generate a response with structured output using function calling"""
        openai_messages = self._prepare_messages(messages)
        api_config = self._prepare_config(config)

        # Create function definition from Pydantic model
        schema = output_model.model_json_schema()
        function_def = {
            "name": "output_structured_data",
            "description": f"Output data in {output_model.__name__} format",
            "parameters": schema,
        }

        try:
            response = await self.client.chat.completions.create(
                messages=openai_messages,
                functions=[function_def],
                function_call={"name": "output_structured_data"},
                **api_config,
            )

            try:
                function_args = response.choices[0].message.function_call.arguments
                return output_model.model_validate_json(function_args)
            except Exception as e:
                raise ValueError(f"Failed to parse structured output: {e}")
        except Exception as e:
            if "401" in str(e) and self.is_project_key:
                raise ValueError(f"Project-based key authentication failed. Please check your OPENAI_PROJECT_ID and ensure the project exists. Error: {e}")
            raise e
