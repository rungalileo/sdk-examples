#!/usr/bin/env python3
"""
Demo script for Startup Simulator 3000
This script demonstrates how to use the application programmatically
"""

import asyncio
import json
import os
from dotenv import load_dotenv
from agent import SimpleAgent
from agent_framework.llm.openai_provider import OpenAIProvider
from agent_framework.llm.models import LLMConfig

# Load environment variables
load_dotenv()

async def demo_silly_mode():
    """Demonstrate silly mode startup generation"""
    print("🎭 DEMO: Silly Mode Startup Generation")
    print("=" * 50)
    
    # Set up the agent
    llm_provider = OpenAIProvider(config=LLMConfig(model="gpt-4", temperature=0.7))
    agent = SimpleAgent(llm_provider=llm_provider, mode="silly")
    
    # Test parameters
    industry = "fintech"
    audience = "millennials"
    random_word = "blockchain"
    
    print(f"Industry: {industry}")
    print(f"Audience: {audience}")
    print(f"Random Word: {random_word}")
    print(f"Mode: Silly")
    print()
    
    # Create task
    task = (
        f"Generate a startup pitch for a {industry} company targeting {audience} "
        f"that includes the word '{random_word}'. Make the pitch creative and "
        f"incorporate relevant trends from HackerNews stories."
    )
    
    try:
        # Run the agent
        result = await agent.run(task, industry=industry, audience=audience, random_word=random_word)
        
        # Parse and display result
        try:
            parsed_result = json.loads(result)
            final_output = parsed_result.get("final_output", result)
        except json.JSONDecodeError:
            final_output = result
        
        print("🎉 Generated Startup Pitch:")
        print("-" * 30)
        print(final_output)
        print("-" * 30)
        
    except Exception as e:
        print(f"❌ Error: {e}")

async def demo_serious_mode():
    """Demonstrate serious mode startup generation"""
    print("\n💼 DEMO: Serious Mode Startup Generation")
    print("=" * 50)
    
    # Set up the agent
    llm_provider = OpenAIProvider(config=LLMConfig(model="gpt-4", temperature=0.7))
    agent = SimpleAgent(llm_provider=llm_provider, mode="serious")
    
    # Test parameters
    industry = "healthcare"
    audience = "small businesses"
    random_word = "AI"
    
    print(f"Industry: {industry}")
    print(f"Audience: {audience}")
    print(f"Random Word: {random_word}")
    print(f"Mode: Serious")
    print()
    
    # Create task
    task = (
        f"Generate a professional startup business plan for a {industry} company "
        f"targeting {audience} that incorporates the concept '{random_word}'. "
        f"Use current business news for market analysis and make this extremely professional."
    )
    
    try:
        # Run the agent
        result = await agent.run(task, industry=industry, audience=audience, random_word=random_word)
        
        # Parse and display result
        try:
            parsed_result = json.loads(result)
            final_output = parsed_result.get("final_output", result)
        except json.JSONDecodeError:
            final_output = result
        
        print("🎉 Generated Business Plan:")
        print("-" * 30)
        print(final_output)
        print("-" * 30)
        
    except Exception as e:
        print(f"❌ Error: {e}")

async def demo_individual_tools():
    """Demonstrate individual tool usage"""
    print("\n🔧 DEMO: Individual Tool Usage")
    print("=" * 50)
    
    # Test startup simulator tool directly
    from tools.startup_simulator import StartupSimulatorTool
    
    print("Testing Startup Simulator Tool:")
    print("-" * 30)
    
    try:
        tool = StartupSimulatorTool()
        result = await tool.execute(
            industry="education",
            audience="students",
            random_word="gamification"
        )
        
        # Parse result
        parsed_result = json.loads(result)
        pitch = parsed_result.get("pitch", "No pitch generated")
        
        print(f"Generated Pitch: {pitch}")
        print(f"Character Count: {parsed_result.get('character_count', 0)}")
        print(f"Timestamp: {parsed_result.get('timestamp', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def check_environment():
    """Check if environment is properly configured"""
    print("🔍 Environment Check")
    print("=" * 50)
    
    # Check required environment variables
    required_vars = ['OPENAI_API_KEY']
    optional_vars = ['NEWS_API_KEY', 'GALILEO_API_KEY', 'GALILEO_PROJECT']
    
    print("Required Variables:")
    for var in required_vars:
        value = os.getenv(var)
        if value and not value.startswith("your-"):
            print(f"  ✅ {var}: Configured")
        else:
            print(f"  ❌ {var}: Not configured")
    
    print("\nOptional Variables:")
    for var in optional_vars:
        value = os.getenv(var)
        if value and not value.startswith("your"):
            print(f"  ✅ {var}: Configured")
        else:
            print(f"  ⚠️  {var}: Not configured (optional)")
    
    print()

async def main():
    """Run all demos"""
    print("🚀 Startup Simulator 3000 - Demo Script")
    print("=" * 60)
    print("This script demonstrates the capabilities of the application")
    print("Make sure you have configured your API keys in .env file")
    print()
    
    # Check environment
    check_environment()
    
    # Check if OpenAI API key is available
    if not os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY").startswith("your-"):
        print("❌ OPENAI_API_KEY not configured. Please edit .env file with your API key.")
        print("Get your API key at: https://platform.openai.com/api-keys")
        return
    
    # Run demos
    try:
        await demo_silly_mode()
        await demo_serious_mode()
        await demo_individual_tools()
        
        print("\n🎉 Demo completed successfully!")
        print("\n💡 Next steps:")
        print("   1. Run 'python app.py' to start the web interface")
        print("   2. Open http://localhost:2021 in your browser")
        print("   3. Try generating your own startup pitches!")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        print("\n💡 Troubleshooting:")
        print("   1. Check your API keys in .env file")
        print("   2. Run 'python test_setup.py' to verify setup")
        print("   3. Make sure all dependencies are installed")

if __name__ == "__main__":
    asyncio.run(main()) 