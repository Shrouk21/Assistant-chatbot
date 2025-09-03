# Assistant Chatbot

A customizable AI assistant chatbot that intelligently determines when additional context is needed and uses web scraping to provide comprehensive, accurate responses.

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Assistant Chatbot                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐    ┌──────────────┐    ┌─────────────────┐│
│  │   User UI   │    │    Agent     │    │   Web Scraper   ││
│  │  (Gradio)   │◄──►│   (LLaMA)    │◄──►│    (Tavily)     ││
│  └─────────────┘    └──────────────┘    └─────────────────┘│
│         │                   │                      │       │
│         │                   │                      │       │
│  ┌─────────────┐    ┌──────────────┐    ┌─────────────────┐│
│  │  Thinking   │    │   Context    │    │    Question     ││
│  │  Process    │    │  Analyzer    │    │  & Answer       ││
│  │  Display    │    │              │    │   Generator     ││
│  └─────────────┘    └──────────────┘    └─────────────────┘│
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## ✨ Features

- **Intelligent Context Detection**: The agent automatically determines when additional context is needed
- **Web Search Integration**: Uses Tavily API for relevant web scraping when context is missing
- **Smart Content Processing**: Splits content into questions and context for effective answering
- **Interactive UI**: Gradio-based interface with real-time thinking process visualization
- **Flexible Model Support**: Compatible with any Ollama model of your choice
- **Local & Cloud Deployment**: Run locally or on Google Colab

## 🚀 Quick Start

### Option 1: Local Setup

1. **Install Ollama** (if running locally)
   ```bash
   # Follow instructions at https://ollama.ai/
   ```

2. **Clone and Configure**
   ```bash
   git clone <your-repo-url>
   cd assistant-chatbot
   cp .env.example .env
   ```

3. **Configure Environment**
   Edit `.env` file:
   Replace first `.env.example` with `.env`
   ```env
   TAVILY_API_KEY=your_tavily_api_key_here
   MODEL_NAME=llama2  # or any ollama model name
   ```

4. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the Application**
   ```bash
   python -m ui.ui
   # OR
   python ui/ui.py
   ```

### Option 2: Google Colab

Use the pre-configured Colab notebook:
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1DoXUXbAmulZmV595qJ0MejcTas1g7LLj?usp=sharing)

## 📋 Requirements

- Python 3.8+
- Ollama (for local deployment)
- Tavily API key
- Dependencies listed in `requirements.txt`

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `TAVILY_API_KEY` | API key for web scraping service | Yes |
| `MODEL_NAME` | Ollama model name (e.g., llama2, codellama) | Yes |

### Supported Models

Any model available through Ollama, including:
- llama2
- codellama
- mistral
- neural-chat
- And more...

## 🎯 How It Works

1. **User Input**: User submits a question through the Gradio interface
2. **Context Analysis**: Agent analyzes if the current context is sufficient
3. **Web Search** (if needed): Tavily API searches for relevant information
4. **Content Processing**: Retrieved content is split into questions and context
5. **Response Generation**: Agent generates a comprehensive answer
6. **UI Display**: Response is shown with thinking process visualization

## 📁 Project Structure

```
assistant-chatbot/
│   .env
│   .gitattributes
│   .gitignore
│   main.py
│   README.md
│   requirements.txt
│
├───agent
│   │   agent_runner.py
│   │   __init__.py
│
├───prompts
│       agent_runner_prompt.txt
│       context_judge_prompt.txt
│       context_relevance_checker.txt
│
├───tests
│   │   test_tools.py
│   │   __init__.py
│
├───tools
│   │   context_presence_judge.py
│   │   context_relevance_checker.py
│   │   context_splitter.py
│   │   web_search_tool.py
│   │   __init__.py
│
└───ui
    │   ui.py
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request


## 🆘 Troubleshooting

### Common Issues

**Ollama connection error**: Ensure Ollama is running locally on default port (11434)
**API key error**: Verify your Tavily API key is correctly set in `.env`
**Module import error**: Make sure all requirements are installed: `pip install -r requirements.txt`

---

*For more detailed setup instructions, check the [Colab notebook](https://colab.research.google.com/drive/1DoXUXbAmulZmV595qJ0MejcTas1g7LLj?usp=sharing)*