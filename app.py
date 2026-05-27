# app.py - COMPLETE AI FAQ CHATBOT WITH WEB SEARCH
import hashlib
import html
import json
import os
import random
import re
import sqlite3
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

import requests
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)
app.secret_key = "ai-faq-chatbot-secret-2024"
app.config["JSON_SORT_KEYS"] = False


@dataclass
class SearchResult:
    answer: str
    source: str
    confidence: float
    category: str
    timestamp: datetime


class LocalKnowledgeBase:
    """Enhanced local knowledge base with multiple domains"""

    def __init__(self):
        self.knowledge = self.load_all_knowledge()
        self.categories = [
            "technology",
            "science",
            "programming",
            "mathematics",
            "history",
            "general",
        ]
        print(f"✓ Loaded local knowledge base with {len(self.knowledge)} entries")

    def load_all_knowledge(self) -> Dict[str, Dict[str, Any]]:
        """Load knowledge from multiple JSON files"""
        knowledge = {}

        # Default knowledge if files don't exist
        default_knowledge = {
            # Technology
            "what is artificial intelligence": {
                "answer": "Artificial Intelligence (AI) is the simulation of human intelligence in machines programmed to think and learn like humans. It includes machine learning, natural language processing, and computer vision.",
                "category": "technology",
                "confidence": 95,
            },
            "what is machine learning": {
                "answer": "Machine Learning is a subset of AI that enables computers to learn and improve from experience without being explicitly programmed. It uses algorithms to parse data, learn from it, and make predictions.",
                "category": "technology",
                "confidence": 95,
            },
            "what is python programming": {
                "answer": "Python is a high-level, interpreted programming language known for its simplicity and readability. It's widely used in web development, data science, AI, and automation.",
                "category": "programming",
                "confidence": 95,
            },
            "what is cloud computing": {
                "answer": "Cloud computing is the delivery of computing services over the internet, including servers, storage, databases, networking, software, and analytics.",
                "category": "technology",
                "confidence": 90,
            },
            # Science
            "what is quantum computing": {
                "answer": "Quantum computing uses quantum-mechanical phenomena like superposition and entanglement to perform computation, potentially solving problems faster than classical computers.",
                "category": "science",
                "confidence": 85,
            },
            "what is dna": {
                "answer": "DNA (Deoxyribonucleic Acid) is the hereditary material in humans and almost all other organisms that carries genetic instructions.",
                "category": "science",
                "confidence": 95,
            },
            "what is photosynthesis": {
                "answer": "Photosynthesis is the process by which green plants and some organisms use sunlight to synthesize foods with carbon dioxide and water, producing oxygen as a byproduct.",
                "category": "science",
                "confidence": 90,
            },
            # Programming
            "what is javascript": {
                "answer": "JavaScript is a programming language used to create interactive effects within web browsers. It's essential for web development alongside HTML and CSS.",
                "category": "programming",
                "confidence": 95,
            },
            "what is an algorithm": {
                "answer": "An algorithm is a set of step-by-step instructions for solving a problem or accomplishing a task. Algorithms are fundamental to computer science.",
                "category": "programming",
                "confidence": 90,
            },
            "what is object oriented programming": {
                "answer": "Object-Oriented Programming (OOP) is a programming paradigm based on the concept of objects, which can contain data and code to manipulate that data.",
                "category": "programming",
                "confidence": 90,
            },
            # Mathematics
            "what is calculus": {
                "answer": "Calculus is a branch of mathematics that studies continuous change, dealing with derivatives, integrals, limits, and infinite series.",
                "category": "mathematics",
                "confidence": 85,
            },
            "what is statistics": {
                "answer": "Statistics is the science of collecting, analyzing, interpreting, presenting, and organizing data to make informed decisions.",
                "category": "mathematics",
                "confidence": 90,
            },
            # General
            "who are you": {
                "answer": "I'm an AI-powered FAQ chatbot designed to answer questions using local knowledge and web search capabilities.",
                "category": "general",
                "confidence": 100,
            },
            "what can you do": {
                "answer": "I can answer questions on various topics including technology, science, programming, and general knowledge. I learn from web searches and user interactions.",
                "category": "general",
                "confidence": 100,
            },
            "how are you": {
                "answer": "I'm functioning optimally! Ready to help you with your questions. How can I assist you today?",
                "category": "general",
                "confidence": 100,
            },
        }

        # Try to load from JSON files
        knowledge_files = {
            "technology": "knowledge_base/tech_knowledge.json",
            "science": "knowledge_base/science_knowledge.json",
            "general": "knowledge_base/general_knowledge.json",
        }

        for category, filepath in knowledge_files.items():
            try:
                if os.path.exists(filepath):
                    with open(filepath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        for key, value in data.items():
                            knowledge[key.lower()] = {
                                "answer": value["answer"],
                                "category": category,
                                "confidence": value.get("confidence", 85),
                            }
                    print(f"  Loaded {len(data)} entries from {filepath}")
            except Exception as e:
                print(f"  Warning: Could not load {filepath}: {e}")

        # Add default knowledge for any missing entries
        for key, value in default_knowledge.items():
            if key not in knowledge:
                knowledge[key] = value

        return knowledge

    def search(self, query: str, threshold: float = 0.3) -> Optional[Dict[str, Any]]:
        """Search for answer in local knowledge base"""
        query_lower = query.lower().strip()

        # Clean the query
        query_clean = self.clean_query(query_lower)

        # Try exact match first
        if query_clean in self.knowledge:
            result = self.knowledge[query_clean].copy()
            result["query"] = query
            result["match_type"] = "exact"
            return result

        # Try partial match
        query_words = set(query_clean.split())

        best_match = None
        best_score = 0

        for key, value in self.knowledge.items():
            key_words = set(key.split())

            # Calculate word overlap
            common_words = query_words.intersection(key_words)
            if common_words:
                # Calculate similarity score
                score = len(common_words) / max(len(query_words), len(key_words), 1)

                if score > best_score and score >= threshold:
                    best_score = score
                    best_match = value.copy()
                    best_match["similarity"] = score
                    best_match["matched_key"] = key
                    best_match["match_type"] = "partial"
                    best_match["query"] = query

        if best_match:
            # Adjust confidence based on similarity
            best_match["confidence"] = best_match["confidence"] * best_score
            return best_match

        return None

    def clean_query(self, query: str) -> str:
        """Clean and normalize query"""
        # Remove common question words
        stop_words = {
            "what",
            "is",
            "are",
            "how",
            "does",
            "do",
            "can",
            "could",
            "would",
            "will",
            "should",
            "tell",
            "me",
            "about",
            "explain",
            "please",
            "the",
            "a",
            "an",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
        }

        # Remove punctuation
        query = re.sub(r"[^\w\s]", " ", query)

        # Split and filter
        words = [w for w in query.split() if w not in stop_words]

        return " ".join(words).strip()

    def get_random_topic(self, category: str = None) -> str:
        """Get a random topic from knowledge base"""
        if category:
            filtered = {
                k: v for k, v in self.knowledge.items() if v["category"] == category
            }
            if filtered:
                return random.choice(list(filtered.keys()))
        return random.choice(list(self.knowledge.keys()))

    def add_knowledge(
        self, question: str, answer: str, category: str = "user", confidence: int = 80
    ):
        """Add new knowledge to the base"""
        key = self.clean_query(question.lower())
        self.knowledge[key] = {
            "answer": answer,
            "category": category,
            "confidence": confidence,
        }

        # Save to user knowledge file
        self.save_user_knowledge(key, answer, category, confidence)

        return True

    def save_user_knowledge(
        self, key: str, answer: str, category: str, confidence: int
    ):
        """Save user-added knowledge to file"""
        try:
            user_file = "knowledge_base/user_knowledge.json"
            data = {}

            if os.path.exists(user_file):
                with open(user_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

            data[key] = {
                "answer": answer,
                "category": category,
                "confidence": confidence,
                "added_date": datetime.now().isoformat(),
            }

            with open(user_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            print(f"Warning: Could not save user knowledge: {e}")


class WebSearchEngine:
    """Web search engine using multiple free APIs"""

    def __init__(self, cache_db: str = "data/cache.db"):
        self.cache_db = cache_db
        self.init_cache()
        self.user_agent = "AIFAQChatbot/1.0 (+https://github.com/aifaqchatbot)"

        # API endpoints
        self.search_apis = [
            self.search_duckduckgo,
            self.search_wikipedia,
            self.search_dictionary,
            self.search_brave,
        ]

    def init_cache(self):
        """Initialize search cache database"""
        os.makedirs("data", exist_ok=True)

        conn = sqlite3.connect(self.cache_db)
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS search_cache (
                query_hash TEXT PRIMARY KEY,
                query TEXT NOT NULL,
                answer TEXT NOT NULL,
                source TEXT NOT NULL,
                confidence REAL,
                category TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                access_count INTEGER DEFAULT 1
            )
        """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS failed_searches (
                query TEXT PRIMARY KEY,
                error_count INTEGER DEFAULT 1,
                last_tried TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        conn.commit()
        conn.close()

    def search_duckduckgo(self, query: str) -> Optional[SearchResult]:
        """Search using DuckDuckGo Instant Answer API"""
        try:
            params = {
                "q": query,
                "format": "json",
                "no_html": "1",
                "skip_disambig": "1",
                "t": "AIFAQBot",
            }

            response = requests.get(
                "https://api.duckduckgo.com/",
                params=params,
                headers={"User-Agent": self.user_agent},
                timeout=8,
            )

            if response.status_code == 200:
                data = response.json()

                # Check Abstract
                if data.get("AbstractText"):
                    abstract = data["AbstractText"].strip()
                    if abstract and len(abstract) > 30:
                        return SearchResult(
                            answer=f"DuckDuckGo: {abstract}",
                            source="DuckDuckGo",
                            confidence=85.0,
                            category=self.detect_category(query),
                            timestamp=datetime.now(),
                        )

                # Check RelatedTopics
                if data.get("RelatedTopics"):
                    for topic in data["RelatedTopics"][:3]:
                        if isinstance(topic, dict) and topic.get("Text"):
                            text = topic["Text"].strip()
                            if text and len(text) > 40:
                                return SearchResult(
                                    answer=f"DuckDuckGo: {text}",
                                    source="DuckDuckGo",
                                    confidence=80.0,
                                    category=self.detect_category(query),
                                    timestamp=datetime.now(),
                                )

                # Check Definition
                if data.get("Definition"):
                    definition = data["Definition"].strip()
                    if definition and len(definition) > 20:
                        return SearchResult(
                            answer=f"DuckDuckGo Definition: {definition}",
                            source="DuckDuckGo",
                            confidence=90.0,
                            category=self.detect_category(query),
                            timestamp=datetime.now(),
                        )

        except Exception as e:
            print(f"DuckDuckGo search error: {type(e).__name__}")

        return None

    def search_wikipedia(self, query: str) -> Optional[SearchResult]:
        """Search using Wikipedia API"""
        try:
            # First, search for page
            search_params = {
                "action": "query",
                "list": "search",
                "srsearch": query,
                "format": "json",
                "srlimit": "3",
            }

            search_response = requests.get(
                "https://en.wikipedia.org/w/api.php",
                params=search_params,
                headers={"User-Agent": self.user_agent},
                timeout=8,
            )

            if search_response.status_code == 200:
                search_data = search_response.json()

                if search_data.get("query", {}).get("search"):
                    # Get first result
                    first_result = search_data["query"]["search"][0]
                    page_title = first_result["title"]

                    # Get page summary
                    summary_params = {
                        "action": "query",
                        "format": "json",
                        "titles": page_title,
                        "prop": "extracts",
                        "exintro": "1",
                        "explaintext": "1",
                        "exchars": "300",
                    }

                    summary_response = requests.get(
                        "https://en.wikipedia.org/w/api.php",
                        params=summary_params,
                        headers={"User-Agent": self.user_agent},
                        timeout=8,
                    )

                    if summary_response.status_code == 200:
                        summary_data = summary_response.json()
                        pages = summary_data.get("query", {}).get("pages", {})

                        for page_id, page_info in pages.items():
                            if "extract" in page_info:
                                extract = page_info["extract"].strip()
                                if extract and len(extract) > 50:
                                    return SearchResult(
                                        answer=f"Wikipedia ({page_title}): {extract}",
                                        source="Wikipedia",
                                        confidence=90.0,
                                        category=self.detect_category(query),
                                        timestamp=datetime.now(),
                                    )

        except Exception as e:
            print(f"Wikipedia search error: {type(e).__name__}")

        return None

    def search_dictionary(self, query: str) -> Optional[SearchResult]:
        """Search using Dictionary API"""
        try:
            # Get first word for dictionary lookup
            first_word = query.split()[0].lower()

            response = requests.get(
                f"https://api.dictionaryapi.dev/api/v2/entries/en/{first_word}",
                headers={"User-Agent": self.user_agent},
                timeout=5,
            )

            if response.status_code == 200:
                data = response.json()

                if isinstance(data, list) and len(data) > 0:
                    first_entry = data[0]

                    if "meanings" in first_entry and first_entry["meanings"]:
                        first_meaning = first_entry["meanings"][0]

                        if (
                            "definitions" in first_meaning
                            and first_meaning["definitions"]
                        ):
                            definition = first_meaning["definitions"][0].get(
                                "definition", ""
                            )

                            if definition:
                                return SearchResult(
                                    answer=f"Dictionary: {definition}",
                                    source="DictionaryAPI",
                                    confidence=75.0,
                                    category="general",
                                    timestamp=datetime.now(),
                                )

        except Exception as e:
            print(f"Dictionary search error: {type(e).__name__}")

        return None

    def search_brave(self, query: str) -> Optional[SearchResult]:
        """Search using Brave Search API (fallback)"""
        try:
            # This is a simplified version - in production, you'd need an API key
            # For now, we'll use a public endpoint

            params = {"q": query, "format": "json"}

            response = requests.get(
                "https://api.search.brave.com/res/v1/web/search",
                params=params,
                headers={"User-Agent": self.user_agent, "Accept": "application/json"},
                timeout=10,
            )

            if response.status_code == 200:
                data = response.json()

                if data.get("web", {}).get("results"):
                    first_result = data["web"]["results"][0]
                    description = first_result.get("description", "")

                    if description:
                        return SearchResult(
                            answer=f"Web Search: {description}",
                            source="Brave Search",
                            confidence=70.0,
                            category=self.detect_category(query),
                            timestamp=datetime.now(),
                        )

        except Exception as e:
            # Brave API often requires key, so this is expected to fail
            pass

        return None

    def detect_category(self, query: str) -> str:
        """Detect query category"""
        query_lower = query.lower()

        tech_keywords = [
            "computer",
            "software",
            "hardware",
            "programming",
            "code",
            "ai",
            "machine learning",
            "algorithm",
            "data",
            "network",
            "python",
            "javascript",
            "java",
            "c++",
            "html",
            "css",
        ]

        science_keywords = [
            "science",
            "physics",
            "chemistry",
            "biology",
            "math",
            "quantum",
            "cell",
            "dna",
            "genetic",
            "evolution",
            "atom",
            "molecule",
            "energy",
            "force",
            "gravity",
        ]

        if any(keyword in query_lower for keyword in tech_keywords):
            return "technology"
        elif any(keyword in query_lower for keyword in science_keywords):
            return "science"
        else:
            return "general"

    def get_cached_result(self, query: str) -> Optional[Dict[str, Any]]:
        """Get cached search result"""
        try:
            query_hash = hashlib.md5(query.lower().encode()).hexdigest()

            conn = sqlite3.connect(self.cache_db)
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT answer, source, confidence, category 
                FROM search_cache 
                WHERE query_hash = ?
            """,
                (query_hash,),
            )

            result = cursor.fetchone()

            if result:
                # Update access stats
                cursor.execute(
                    """
                    UPDATE search_cache 
                    SET last_accessed = CURRENT_TIMESTAMP,
                        access_count = access_count + 1
                    WHERE query_hash = ?
                """,
                    (query_hash,),
                )

                conn.commit()
                conn.close()

                return {
                    "answer": result[0],
                    "source": result[1],
                    "confidence": result[2],
                    "category": result[3],
                    "cached": True,
                }

            conn.close()

        except Exception as e:
            print(f"Cache error: {e}")

        return None

    def cache_result(self, query: str, result: SearchResult):
        """Cache search result"""
        try:
            query_hash = hashlib.md5(query.lower().encode()).hexdigest()

            conn = sqlite3.connect(self.cache_db)
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT OR REPLACE INTO search_cache 
                (query_hash, query, answer, source, confidence, category)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    query_hash,
                    query,
                    result.answer,
                    result.source,
                    result.confidence,
                    result.category,
                ),
            )

            conn.commit()
            conn.close()

        except Exception as e:
            print(f"Cache save error: {e}")

    def search(self, query: str) -> Optional[Dict[str, Any]]:
        """Perform web search with caching"""
        print(f"  🌐 Searching web for: '{query}'")

        # Check cache first
        cached = self.get_cached_result(query)
        if cached:
            print(f"  ✓ Found in cache ({cached['source']})")
            return cached

        # Check if this query has failed recently
        if self.is_recent_failure(query):
            print(f"  ⚠ Skipping recently failed query")
            return None

        # Try each search API in order
        for search_api in self.search_apis:
            try:
                result = search_api(query)
                if result:
                    print(f"  ✓ Found via {result.source}")

                    # Cache the result
                    self.cache_result(query, result)

                    return {
                        "answer": result.answer,
                        "source": result.source,
                        "confidence": result.confidence,
                        "category": result.category,
                        "cached": False,
                    }

                # Small delay between API calls
                time.sleep(0.5)

            except Exception as e:
                print(f"  ⚠ API error: {type(e).__name__}")
                continue

        # Mark as failed
        self.record_failure(query)
        print(f"  ✗ No results found from web")
        return None

    def is_recent_failure(self, query: str) -> bool:
        """Check if query failed recently"""
        try:
            conn = sqlite3.connect(self.cache_db)
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT error_count, last_tried 
                FROM failed_searches 
                WHERE query = ?
            """,
                (query,),
            )

            result = cursor.fetchone()
            conn.close()

            if result:
                error_count, last_tried = result
                last_tried = datetime.fromisoformat(last_tried)

                # If failed more than 3 times in last hour, skip
                if error_count >= 3 and (datetime.now() - last_tried).seconds < 3600:
                    return True

        except Exception as e:
            print(f"is_recent_failure error: {e}")
            return False

        return False

    def record_failure(self, query: str):
        """Record failed search"""
        try:
            conn = sqlite3.connect(self.cache_db)
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO failed_searches (query, error_count, last_tried)
                VALUES (?, 1, CURRENT_TIMESTAMP)
                ON CONFLICT(query) DO UPDATE SET
                    error_count = error_count + 1,
                    last_tried = CURRENT_TIMESTAMP
            """,
                (query,),
            )

            conn.commit()
            conn.close()

        except Exception as e:
            print(f"Failed to record failure: {e}")


class AIFAQChatbot:
    """Main AI FAQ Chatbot class"""

    def __init__(self):
        print("=" * 70)
        print("🤖 AI FAQ CHATBOT INITIALIZING")
        print("=" * 70)

        # Initialize components
        self.knowledge_base = LocalKnowledgeBase()
        self.web_search = WebSearchEngine()

        # Load configuration
        self.config = self.load_config()

        # Initialize conversation tracking
        self.conversation_history = []

        print("\n✓ Components initialized:")
        print(f"  • Local Knowledge: {len(self.knowledge_base.knowledge)} entries")
        print(f"  • Web Search: {len(self.web_search.search_apis)} APIs")
        print(f"  • Cache Database: Ready")
        print("\n" + "-" * 70)

    def load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        default_config = {
            "search_enabled": True,
            "cache_enabled": True,
            "confidence_threshold": 40,
            "max_history": 50,
            "response_timeout": 10,
            "auto_learn": True,
            "suggestions_enabled": True,
        }

        try:
            if os.path.exists("config.json"):
                with open("config.json", "r") as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
        except Exception as e:
            print(f"Warning: Could not load config: {e}")

        return default_config

    def process_query(self, query: str) -> Dict[str, Any]:
        """Process user query and return response"""
        start_time = time.time()

        print(f"\n📨 Processing: '{query}'")

        # Step 1: Check local knowledge base
        local_result = self.knowledge_base.search(query)

        if (
            local_result
            and local_result["confidence"] >= self.config["confidence_threshold"]
        ):
            response_time = time.time() - start_time

            print(f"  ✓ Found in local knowledge")
            print(f"     Category: {local_result['category']}")
            print(f"     Confidence: {local_result['confidence']:.1f}%")

            return {
                "answer": local_result["answer"],
                "source": "Local Knowledge",
                "confidence": local_result["confidence"],
                "category": local_result["category"],
                "response_time": round(response_time, 3),
                "method": local_result.get("match_type", "exact"),
                "learned": False,
                "suggestions": self.generate_suggestions(local_result["category"]),
            }

        # Step 2: Try web search if enabled
        if self.config["search_enabled"]:
            web_result = self.web_search.search(query)

            if web_result:
                response_time = time.time() - start_time

                print(f"  ✓ Found via web search")
                print(f"     Source: {web_result['source']}")
                print(f"     Confidence: {web_result['confidence']}%")

                # Auto-learn if enabled
                learned = False
                if self.config["auto_learn"] and web_result["confidence"] > 70:
                    learned = self.knowledge_base.add_knowledge(
                        query,
                        web_result["answer"],
                        web_result["category"],
                        int(web_result["confidence"]),
                    )
                    if learned:
                        print(f"     📚 Auto-learned to knowledge base")

                return {
                    "answer": web_result["answer"],
                    "source": web_result["source"],
                    "confidence": web_result["confidence"],
                    "category": web_result["category"],
                    "response_time": round(response_time, 3),
                    "method": "web_search",
                    "learned": learned,
                    "cached": web_result.get("cached", False),
                    "suggestions": self.generate_suggestions(web_result["category"]),
                }

        # Step 3: Generate fallback response
        response_time = time.time() - start_time

        print(f"  ⚠ No specific answer found")

        fallback = self.generate_fallback_response(query)

        return {
            "answer": fallback["answer"],
            "source": "AI Generated",
            "confidence": fallback["confidence"],
            "category": fallback["category"],
            "response_time": round(response_time, 3),
            "method": "fallback",
            "learned": False,
            "suggestions": fallback["suggestions"],
        }

    def generate_fallback_response(self, query: str) -> Dict[str, Any]:
        """Generate intelligent fallback response"""
        category = self.web_search.detect_category(query)

        # Get related topics from knowledge base
        related = []
        query_words = set(self.knowledge_base.clean_query(query.lower()).split())

        for key in self.knowledge_base.knowledge.keys():
            key_words = set(key.split())
            if query_words.intersection(key_words):
                related.append(key)

        # Limit to 5 related topics
        related = list(set(related))[:5]

        if related:
            suggestions = [f"Try asking about: '{topic}'" for topic in related]
            suggestions_text = "\n\n💡 " + "\n• ".join(suggestions)

            answer = f"I don't have a specific answer for '{query}', but I can help with related topics.{suggestions_text}"
        else:
            # Get random topics from the detected category
            random_topics = []
            for _ in range(3):
                topic = self.knowledge_base.get_random_topic(category)
                if topic and topic not in random_topics:
                    random_topics.append(topic)

            if random_topics:
                suggestions = [f"• What is {topic}?" for topic in random_topics]
                suggestions_text = "\n\n💡 You might ask:\n" + "\n".join(suggestions)
            else:
                suggestions_text = "\n\n💡 Try asking about technology, science, or general knowledge topics."

            answer = f"I couldn't find information about '{query}'.{suggestions_text}"

        return {
            "answer": answer,
            "confidence": 0.0,
            "category": category,
            "suggestions": related if related else random_topics,
        }

    def generate_suggestions(self, category: str) -> List[str]:
        """Generate follow-up suggestions"""
        suggestions = []

        # Get 3 random topics from the same category
        for _ in range(3):
            topic = self.knowledge_base.get_random_topic(category)
            if topic and topic not in suggestions:
                suggestions.append(f"What is {topic}?")

        return suggestions[:3]

    def get_stats(self) -> Dict[str, Any]:
        """Get chatbot statistics"""
        try:
            conn = sqlite3.connect(self.web_search.cache_db)
            cursor = conn.cursor()

            # Cache stats
            cursor.execute("SELECT COUNT(*) FROM search_cache")
            cache_count = cursor.fetchone()[0]

            cursor.execute("SELECT SUM(access_count) FROM search_cache")
            total_accesses = cursor.fetchone()[0] or 0

            conn.close()

            return {
                "knowledge_base_entries": len(self.knowledge_base.knowledge),
                "cached_answers": cache_count,
                "total_accesses": total_accesses,
                "search_enabled": self.config["search_enabled"],
                "categories": self.knowledge_base.categories,
                "web_apis": len(self.web_search.search_apis),
            }

        except Exception as e:
            print(f"Stats error: {e}")
            return {
                "knowledge_base_entries": len(self.knowledge_base.knowledge),
                "search_enabled": self.config["search_enabled"],
            }

    def clear_cache(self) -> bool:
        """Clear search cache"""
        try:
            conn = sqlite3.connect(self.web_search.cache_db)
            cursor = conn.cursor()

            cursor.execute("DELETE FROM search_cache")
            cursor.execute("DELETE FROM failed_searches")

            conn.commit()
            conn.close()

            return True

        except Exception as e:
            print(f"Clear cache error: {e}")
            return False


# Initialize chatbot globally
print("\n🚀 Starting AI FAQ Chatbot Server...")
chatbot = AIFAQChatbot()


@app.route("/")
def home():
    """Render the main chat interface"""
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat_endpoint():
    """Handle chat requests"""
    try:
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400

        data = request.json
        user_input = data.get("message", "").strip()

        if not user_input:
            return jsonify({"error": "Empty message"}), 400

        # Process query
        response = chatbot.process_query(user_input)

        # Add to conversation history
        chatbot.conversation_history.append(
            {
                "query": user_input,
                "response": response,
                "timestamp": datetime.now().isoformat(),
            }
        )

        # Limit history size
        if len(chatbot.conversation_history) > chatbot.config["max_history"]:
            chatbot.conversation_history = chatbot.conversation_history[
                -chatbot.config["max_history"] :
            ]

        # Prepare response
        result = {
            "answer": html.escape(response["answer"]).replace("\n", "<br>"),
            "source": response["source"],
            "confidence": round(response["confidence"], 1),
            "category": response["category"],
            "response_time": response["response_time"],
            "method": response["method"],
            "learned": response.get("learned", False),
            "cached": response.get("cached", False),
            "suggestions": response.get("suggestions", []),
            "status": "success",
        }

        print(f"  ✅ Response ready in {response['response_time']}s")
        print("=" * 70)

        return jsonify(result)

    except Exception as e:
        print(f"\n❌ Error in chat endpoint: {str(e)}")
        import traceback

        traceback.print_exc()

        return (
            jsonify(
                {
                    "error": "Internal server error",
                    "answer": "Sorry, I encountered an error while processing your request. Please try again.",
                    "source": "error",
                    "confidence": 0.0,
                    "status": "error",
                }
            ),
            500,
        )


@app.route("/stats", methods=["GET"])
def stats_endpoint():
    """Get chatbot statistics"""
    stats = chatbot.get_stats()

    return jsonify(
        {
            "status": "online",
            "timestamp": datetime.now().isoformat(),
            "stats": stats,
            "features": [
                "Local knowledge base search",
                "Multi-API web search (DuckDuckGo, Wikipedia, Dictionary)",
                "Intelligent caching system",
                "Self-learning from web results",
            ],
        }
    )


@app.route("/clear-cache", methods=["POST"])
def clear_cache_endpoint():
    """Clear search cache"""
    try:
        success = chatbot.clear_cache()

        if success:
            return jsonify(
                {"status": "success", "message": "Search cache cleared successfully"}
            )

        return jsonify({"error": "Failed to clear cache"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/search", methods=["POST"])
def direct_search():
    """Direct web search endpoint"""
    try:
        data = request.json
        query = data.get("query", "").strip()

        if not query:
            return jsonify({"error": "Query required"}), 400

        result = chatbot.web_search.search(query)

        if result:
            return jsonify({"status": "success", "query": query, "result": result})

        return jsonify(
            {
                "status": "not_found",
                "query": query,
                "message": "No results found from web search",
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify(
        {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "service": "AI FAQ Chatbot",
            "version": "1.0.0",
        }
    )


if __name__ == "__main__":
    # Create necessary directories
    os.makedirs("templates", exist_ok=True)
    os.makedirs("knowledge_base", exist_ok=True)
    os.makedirs("data", exist_ok=True)

    print("\n" + "=" * 70)
    print("🌐 WEB SERVER STARTING")
    print("=" * 70)
    print("\n📡 Server: http://localhost:5000")
    print("📊 Stats: http://localhost:5000/stats")
    print("🏥 Health: http://localhost:5000/health")
    print("\n💡 Test Questions:")
    print("  • What is artificial intelligence?")
    print("  • Explain quantum computing")
    print("  • How does photosynthesis work?")
    print("  • What is Python programming?")
    print("\n" + "-" * 70)

    app.run(debug=True, host="0.0.0.0", port=5000, use_reloader=False)
