# 🚀 Startup Simulator 3000

An 8-bit styled AI-powered startup pitch generator that creates either silly, creative
pitches or professional business proposals. Built with a custom agentic framework
powered by OpenAI and monitored with Galileo observability.

This is a **complete, self-contained version** that you can copy to any directory and
run immediately!

![Powered by Galileo](static/images/05-25-Galileo-Logo-Primary-Horizontal-Light.png)

## ✨ Features

### 🎭 Dual Modes

- **Silly Mode**: Generates absurd, creative startup pitches inspired by HackerNews
  trends
- **Serious Mode**: Creates professional, corporate business proposals with market
  analysis from NewsAPI

### 🎮 8-bit Web Interface

- Retro pixel art styling with vibrant color scheme
- Animated backgrounds and glowing text effects
- Responsive design for desktop and mobile
- Interactive mode selection and form validation

### 🤖 Custom Agent Framework

- Multi-tool agent architecture built from scratch
- Dynamic tool selection based on execution mode
- Comprehensive input validation and error handling
- Real-time context fetching from external APIs
- Custom tool registry and execution system

### 📊 Galileo Observability

- Complete workflow and tool execution logging
- Structured JSON output for debugging and analysis
- LLM call tracking with token usage and performance metrics
- Distributed tracing across the entire execution pipeline

## 🚀 Quick Start Guide

### Step 1: Prerequisites

Make sure you have:

- **Python 3.10+** installed on your system
- **Git** (optional, for cloning)
- **A code editor** (VS Code, PyCharm, etc.)

### Step 2: Copy This Folder

Simply copy this entire `startup-sim-3000-standalone` folder to wherever you want to
run it!

### Step 3: Set Up Python Environment

```bash
# Navigate to the folder
cd startup-sim-3000-standalone

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 4: Configure API Keys

From within your code editor of choice, copy the `.example.env` file to `.env` and
fill in the values. Don't forget to add the `.env` file to your `.gitignore` file.

**Required API Keys:**

- **OpenAI API Key**: Get one at
  [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
- **NewsAPI Key**: Get one at
  [https://newsapi.org/register](https://newsapi.org/register) (for serious mode)
- **Galileo API Key**: Get one at
  [https://console.galileo.ai/](https://console.galileo.ai/) (for observability)

Your `.env` file should look like this:

```env
# Galileo Environment Variables
GALILEO_API_KEY=your-galileo-api-key             # Your Galileo API key.
GALILEO_PROJECT=your-galileo-project-name        # Your Galileo project name.
GALILEO_LOG_STREAM=your-galileo-log-stream       # The name of the log stream you want to use for logging.

# Provide the console url below if you are using a custom deployment, and not using app.galileo.ai
# GALILEO_CONSOLE_URL=your-galileo-console-url   # Optional if you are using a hosted version of Galileo

# Required API Keys
OPENAI_API_KEY=sk-your-openai-key-here
NEWS_API_KEY=your-newsapi-key-here

# Optional Configuration
LLM_MODEL=gpt-4
LLM_TEMPERATURE=0.7
VERBOSITY=low
ENVIRONMENT=development
ENABLE_LOGGING=true
```

### Step 5: Run the Application

```bash
# Start the web server
python app.py
```

### Step 6: Open Your Browser

Navigate to: **http://localhost:2021**

You should see the Startup Sim 3000 web interface! 🎉

## 🎯 How to Use

### Web Interface

1. **Choose Mode**: Select either "🎭 SILLY MODE" or "💼 SERIOUS MODE"
2. **Fill in Details**:
   - **Industry**: What industry your startup is in (e.g., "fintech", "healthcare",
     "education")
   - **Target Audience**: Who you're targeting (e.g., "millennials", "small
     businesses", "developers")
   - **Random Word**: A word to include in your pitch (e.g., "blockchain", "AI",
     "sustainability")
3. **Generate**: Click the "Generate Startup Pitch" button
4. **Enjoy**: Read your creative or professional startup pitch!

### Command Line (Alternative)

```bash
# Run the CLI version
python run_startup_sim.py
```

## 🏗️ Project Structure

```
startup-sim-3000-standalone/
├── app.py                 # Main Flask application
├── agent.py              # Core agent implementation
├── tools.json            # Tool configuration
├── requirements.txt      # Python dependencies
├── .env.example         # Environment variables template
├── .gitignore           # Git ignore patterns
├── README.md            # This file
├── TUTORIAL.md          # Detailed tutorial
├── agent_framework/     # Custom agent framework
│   ├── agent.py         # Base Agent class
│   ├── models.py        # Data models and schemas
│   ├── config.py        # Configuration management
│   ├── exceptions.py    # Custom exceptions
│   ├── llm/            # LLM providers (OpenAI)
│   ├── tools/          # Tool base classes
│   ├── prompts/        # Prompt templates
│   └── utils/          # Utility functions
├── tools/              # Tool implementations
│   ├── startup_simulator.py
│   ├── serious_startup_simulator.py
│   ├── hackernews_tool.py
│   └── news_api_tool.py
├── templates/          # HTML templates
│   ├── index.html      # Main web interface
│   ├── instructions.html
│   └── credits.html
└── static/            # Static assets
    ├── css/           # Stylesheets
    ├── js/            # JavaScript
    └── images/        # Images and logos
```

## 🔧 Troubleshooting

### Common Issues

**1. "Module not found" errors**

```bash
# Make sure you're in the virtual environment
# Your prompt should show (venv)
source venv/bin/activate  # or venv\Scripts\activate on Windows
```

**2. "OPENAI_API_KEY not set" error**

```bash
# Check your .env file exists and has the correct key
cat .env
# Make sure OPENAI_API_KEY=sk-your-actual-key-here
```

**3. Port 2021 already in use**

```bash
# Change the port in app.py or kill the existing process
# In app.py, change: app.run(debug=True, host='0.0.0.0', port=2021)
# to: app.run(debug=True, host='0.0.0.0', port=2022)
```

**4. Galileo logging not working**

- This is optional! The app will work without Galileo
- If you want Galileo, make sure your API key and project are set correctly

### Getting Help

1. **Check the logs**: Look at the terminal output for error messages
2. **Verify API keys**: Make sure all required API keys are set in `.env`
3. **Check Python version**: Ensure you're using Python 3.8+
4. **Reinstall dependencies**: `pip install -r requirements.txt --force-reinstall`

## 🎓 Learning Resources

### For Beginners

- **Python Basics**:
  [Python.org Tutorial](https://docs.python.org/3/tutorial/)
- **Flask Web Framework**:
  [Flask Documentation](https://flask.palletsprojects.com/)
- **Async Programming**:
  [Python AsyncIO Tutorial](https://docs.python.org/3/library/asyncio.html)

### For AI/ML Developers

- **OpenAI API**:
  [OpenAI Documentation](https://platform.openai.com/docs)
- **Custom Agent Development**: Study the `agent_framework/` directory to understand
  agent architecture
- **Galileo Observability**:
  [Galileo Documentation](https://docs.galileo.ai/)

### For Web Developers

- **HTML/CSS/JavaScript**:
  [MDN Web Docs](https://developer.mozilla.org/)
- **Responsive Design**:
  [CSS Grid and Flexbox](https://css-tricks.com/snippets/css/complete-guide-grid/)

### For Agent Framework Development

- **Custom Tool Development**: Study the tools in the `tools/` directory
- **Agent Architecture**: Examine `agent_framework/agent.py` for the base Agent class
- **Observability Patterns**: Learn from the Galileo integration in each tool

## 🤝 Contributing

This is a standalone version, but if you want to contribute to the main project:

1. Fork the original repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 🙏 Acknowledgments

- **OpenAI** for providing the GPT models
- **Galileo** for observability and monitoring
- **NewsAPI** for business news data
- **HackerNews** for tech community trends
- **Flask** for the web framework
- **Custom Agent Framework** for demonstrating agent architecture from scratch

## 📞 Support

If you run into issues:

1. Check the troubleshooting section above
2. Look at the terminal logs for error messages
3. Verify your API keys are correct
4. Make sure you're using Python 3.10+

---

**Happy Startup Pitching! 🚀**

*Built with ❤️ and silliness for those exploring the world of AI*  