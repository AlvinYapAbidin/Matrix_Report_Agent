# Matrix th AI Agent that writes reports

An AI-powered essay writer using LangGraph for multi-agent orchestration. This project demonstrates how to build intelligent, collaborative AI agents that can work together to create high-quality essays.

## Features

- **Multi-Agent Architecture**: Uses LangGraph to orchestrate multiple AI agents
- **Essay Writing Pipeline**: Automated essay generation with research and refinement
- **Streamlit Interface**: User-friendly web interface for interacting with the system
- **Research Integration**: Connects to external sources for up-to-date information
- **Modular Design**: Clean, extensible architecture for adding new capabilities

## Requirements

- Python 3.9 or higher
- OpenAI API key
- Tavily API key (for research)

## Installation

1. Clone the repository:
```bash
git clone git@github.com:AlvinYapAbidin/Matrix_Report_Agent.git
cd AI_Agents_in_Langraph
```

2. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -e .
```

## Configuration

1. Create a `.env` file in the project root:
```env
OPENAI_API_KEY=your_openai_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

2. Get your API keys:
   - [OpenAI API Key](https://platform.openai.com/api-keys)
   - [Tavily API Key](https://tavily.com/)

## Usage

### Running the Streamlit App

```bash
streamlit run app.py
```

### Using the Essay Writer

```python
from essay_writer import EssayWriter

writer = EssayWriter()
essay = writer.write_essay(
    topic="The Future of Artificial Intelligence",
    word_count=1000
)
print(essay)
```

## Project Structure

```
AI_Agents_in_Langraph/
├── app.py                 # Streamlit application entry point
├── essay_writer/          # Core essay writing module
│   ├── __init__.py
│   ├── clients.py         # API client implementations
│   ├── graph.py           # LangGraph workflow definitions
│   ├── prompts.py         # AI prompt templates
│   └── schema.py          # Data models and schemas
├── essay_writer.py        # Main essay writer interface
├── helper.py              # Utility functions
├── pyproject.toml         # Project configuration
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Architecture

The system uses a multi-agent approach where different AI agents handle specific tasks:

1. **Research Agent**: Gathers information from external sources
2. **Outline Agent**: Creates structured essay outlines
3. **Writing Agent**: Generates initial essay content
4. **Refinement Agent**: Improves and polishes the final essay

All agents are orchestrated using LangGraph, which manages the workflow and agent interactions.

## Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black .
isort .
```

### Linting

```bash
flake8
mypy .
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with [LangGraph](https://github.com/langchain-ai/langgraph)
- Powered by [OpenAI](https://openai.com/)
- Research capabilities provided by [Tavily](https://tavily.com/)

## Support

If you encounter any issues or have questions, please:

1. Check the existing issues
2. Create a new issue with detailed information
3. Include your Python version and error messages

---

**Note**: This project requires Python 3.9+ due to LangGraph dependencies.
