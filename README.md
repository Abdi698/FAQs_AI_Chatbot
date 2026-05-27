# 🤖 AI FAQ Chatbot

A sophisticated AI-powered FAQ chatbot with web search capabilities, built with Flask. This chatbot combines local knowledge bases with real-time web search to provide accurate, contextual answers across multiple domains including technology, science, programming, and general knowledge.

## ✨ Features

### Core Capabilities

- **Local Knowledge Base**: Pre-loaded with comprehensive Q&A across multiple categories
- **Real-time Web Search**: Integrates with multiple APIs (DuckDuckGo, Wikipedia, Dictionary API)
- **Intelligent Caching**: Reduces API calls and improves response times
- **Self-Learning**: Automatically learns from web search results
- **Category Detection**: Automatically categorizes queries and responses
- **Conversation History**: Tracks and limits conversation history
- **REST API**: Full REST API for integration with other systems

### Knowledge Categories

- **Technology**: AI, Machine Learning, Cloud Computing, etc.
- **Science**: Quantum Computing, DNA, Photosynthesis, etc.
- **Programming**: Python, JavaScript, Algorithms, OOP, etc.
- **Mathematics**: Calculus, Statistics
- **General**: Common questions and conversational responses

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Internet connection for web search functionality

### Installation

1. **Clone or download the project**

   ```bash
   cd faq_ai_chatbot
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**

   ```bash
   python app.py
   ```

4. **Open your browser**
   ```
   http://localhost:5000
   ```

## 📁 Project Structure

```
faq_ai_chatbot/
├── app.py                    # Main Flask application
├── config.json              # Configuration settings
├── faq_data.json            # FAQ data and settings
├── requirements.txt         # Python dependencies
├── templates/
│   └── index.html           # Web interface
├── knowledge_base/          # Knowledge base files
│   ├── general_knowledge.json
│   ├── science_knowledge.json
│   ├── tech_knowledge.json
│   └── user_knowledge.json   # User-added knowledge
├── data/                    # Application data
│   └── cache.db             # Search cache database
└── screenshot that show how system works/  # Screenshots
```

## 🔧 Configuration

The `config.json` file allows you to customize various aspects:

```json
{
  "search_enabled": true, // Enable/disable web search
  "cache_enabled": true, // Enable/disable caching
  "confidence_threshold": 40, // Minimum confidence for answers
  "max_history": 50, // Maximum conversation history
  "response_timeout": 10, // Response timeout in seconds
  "auto_learn": true, // Auto-learn from web results
  "suggestions_enabled": true, // Enable follow-up suggestions
  "web_search_timeout": 8, // Web search timeout
  "max_cache_age_days": 30, // Cache expiration
  "enable_duckduckgo": true, // Enable DuckDuckGo search
  "enable_wikipedia": true, // Enable Wikipedia search
  "enable_dictionary": true // Enable Dictionary API
}
```

## 🌐 API Endpoints

### Chat Interface

- `GET /` - Main chat interface
- `POST /chat` - Send chat message
- `GET /stats` - Get chatbot statistics
- `POST /clear-cache` - Clear search cache
- `POST /search` - Direct web search
- `GET /health` - Health check

### Example API Usage

**Send a chat message:**

```bash
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is artificial intelligence?"}'
```

## 💡 Usage Examples

### Sample Questions

- "What is artificial intelligence?"
- "Explain quantum computing"
- "How does photosynthesis work?"
- "What is Python programming?"
- "Who are you?" (conversational)
- "What can you do?" (capabilities)

## 🔍 How It Works

1. **Query Processing**: User input is cleaned and normalized
2. **Local Search**: First checks the local knowledge base for exact/partial matches
3. **Web Search**: If no local match found, searches multiple web APIs
4. **Caching**: Results are cached to improve performance
5. **Auto-Learning**: High-confidence web results are added to local knowledge
6. **Response Generation**: Returns answer with confidence score, source, and suggestions

### Search Strategy

- **Exact Match**: Direct lookup in knowledge base
- **Partial Match**: Word overlap similarity scoring
- **Web Search**: Multi-API fallback (DuckDuckGo → Wikipedia → Dictionary → Brave)
- **Fallback**: Intelligent suggestions when no answer found

## 🛠️ Technical Details

### Dependencies

- **Flask 2.3.3**: Web framework
- **Requests 2.31.0**: HTTP client for API calls

### Architecture

- **LocalKnowledgeBase**: Manages static and user-added knowledge
- **WebSearchEngine**: Handles multi-API web search with caching
- **AIFAQChatbot**: Main orchestrator class
- **Flask App**: REST API and web interface

### Database

- **SQLite**: Used for search result caching and failure tracking
- **JSON Files**: Knowledge base storage

### Performance Features

- **Intelligent Caching**: Reduces API calls and response times
- **Failure Tracking**: Avoids repeatedly searching failed queries
- **Response Timeouts**: Prevents hanging on slow APIs
- **Background Processing**: Non-blocking search operations

## 📊 Monitoring

### Statistics Endpoint

Access `http://localhost:5000/stats` for:

- Knowledge base entry count
- Cached answer count
- Total cache accesses
- Available categories
- Web API status

### Health Check

`GET /health` returns service status and version information.

## 🔧 Troubleshooting

### Common Issues

**Web search not working:**

- Check internet connection
- Verify API endpoints are accessible
- Check `config.json` for disabled search options

**Slow responses:**

- Clear cache: `POST /clear-cache`
- Check `web_search_timeout` in config
- Verify API rate limits

**Knowledge not saving:**

- Check write permissions for `knowledge_base/` directory
- Verify API request formats

### Logs

The application prints detailed logs to the console including:

- Query processing steps
- Search results and sources
- Cache hits/misses
- Learning events
- Error messages

## 🤝 Contributing

### Adding Knowledge

1. Edit JSON files in `knowledge_base/` directory
2. Submit via API endpoint or update the knowledge library directly

### Code Contributions

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## 📄 License

This project is open source. Feel free to use, modify, and distribute.

## 🙏 Acknowledgments

- Built with Flask web framework
- Uses free APIs: DuckDuckGo, Wikipedia, Dictionary API
- Inspired by modern chatbot architectures

---

**Version**: 1.0.0
**Last Updated**: March 2026
**Author**: AI FAQ Chatbot Project</content>
<filePath>c:\Users\user\Desktop\4th year material\faq_ai_chatbot\README.md
