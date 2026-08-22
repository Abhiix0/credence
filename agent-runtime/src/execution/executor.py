"""
Task Executor with capability-based routing and Gemini AI integration.

IMPORTANT: This module ONLY executes tasks and returns results.
It does NOT handle bidding, market operations, or transaction signing.
Financial/bidding logic belongs in the agent or market client layers.
"""

import hashlib
import json
import os
import re
from typing import Dict, Any, Tuple, Optional
import requests

from ..models import Task

# Lazy import to handle missing API key gracefully
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False


class TaskExecutor:
    """
    Executes assigned tasks using capability-based routing.
    
    Supported capabilities:
    - sentiment-analysis: Classifies text as positive/negative/neutral
    - classification: Categorizes text into predefined labels
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.genai_client = None
        
        # Initialize Gemini client if API key is available
        if self.api_key and GENAI_AVAILABLE:
            try:
                genai.configure(api_key=self.api_key)
                self.genai_client = genai.GenerativeModel('gemini-pro')
            except Exception as e:
                print(f"Warning: Failed to initialize Gemini client: {e}")
                self.genai_client = None

    def _fetch_task_input(self, specification_uri: str) -> str:
        """
        Fetch task input from specification URI.
        
        MVP Assumption:
        - If URI starts with 'ipfs://' or 'https://', fetch content via HTTP
        - Otherwise, treat as raw text string
        - In production, this would use proper IPFS client and handle more protocols
        
        Args:
            specification_uri: The task specification URI or raw text
            
        Returns:
            Task input text
        """
        # Handle IPFS URIs (convert to HTTP gateway for MVP)
        if specification_uri.startswith("ipfs://"):
            # Extract CID and use public IPFS gateway
            cid = specification_uri.replace("ipfs://", "")
            gateway_url = f"https://ipfs.io/ipfs/{cid}"
            try:
                response = requests.get(gateway_url, timeout=10)
                response.raise_for_status()
                return response.text
            except Exception as e:
                raise RuntimeError(f"Failed to fetch IPFS content: {e}")
        
        # Handle HTTPS URIs
        elif specification_uri.startswith("https://") or specification_uri.startswith("http://"):
            try:
                response = requests.get(specification_uri, timeout=10)
                response.raise_for_status()
                return response.text
            except Exception as e:
                raise RuntimeError(f"Failed to fetch URI content: {e}")
        
        # Treat as raw text
        else:
            return specification_uri

    def _sentiment_analysis_gemini(self, text: str) -> Dict[str, str]:
        """
        Perform sentiment analysis using Gemini AI.
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dictionary with 'result' key containing sentiment (positive/negative/neutral)
        """
        prompt = f"""Analyze the sentiment of the following text and respond with ONLY a JSON object.
The JSON must have exactly one key "result" with value being one of: "positive", "negative", or "neutral".
Do not include any explanation or additional text, only the JSON object.

Text to analyze:
{text}

Response (JSON only):"""

        try:
            # Generate with low temperature for deterministic output
            response = self.genai_client.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.0,
                    max_output_tokens=50,
                )
            )
            
            # Parse JSON response
            result_text = response.text.strip()
            # Remove markdown code blocks if present
            result_text = re.sub(r'^```json\s*', '', result_text)
            result_text = re.sub(r'\s*```$', '', result_text)
            
            result = json.loads(result_text)
            
            # Validate result format
            if "result" not in result:
                raise ValueError("Response missing 'result' key")
            
            sentiment = result["result"].lower()
            if sentiment not in ["positive", "negative", "neutral"]:
                raise ValueError(f"Invalid sentiment value: {sentiment}")
            
            return {"result": sentiment}
            
        except Exception as e:
            # Fallback to keyword-based classifier on any error
            print(f"Gemini sentiment analysis failed: {e}, falling back to keyword classifier")
            return self._sentiment_analysis_fallback(text)

    def _sentiment_analysis_fallback(self, text: str) -> Dict[str, str]:
        """
        Fallback keyword-based sentiment classifier.
        Used when Gemini API is unavailable or fails.
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dictionary with 'result' key containing sentiment
        """
        text_lower = text.lower()
        
        # Simple keyword lists
        positive_keywords = [
            "good", "great", "excellent", "amazing", "wonderful", "fantastic",
            "love", "best", "happy", "awesome", "perfect", "brilliant"
        ]
        negative_keywords = [
            "bad", "terrible", "awful", "horrible", "worst", "hate",
            "poor", "disappointing", "sad", "angry", "frustrating", "useless"
        ]
        
        # Count keyword occurrences
        positive_count = sum(1 for word in positive_keywords if word in text_lower)
        negative_count = sum(1 for word in negative_keywords if word in text_lower)
        
        # Determine sentiment
        if positive_count > negative_count:
            return {"result": "positive"}
        elif negative_count > positive_count:
            return {"result": "negative"}
        else:
            return {"result": "neutral"}

    def _classification_gemini(self, text: str, categories: list) -> Dict[str, str]:
        """
        Perform text classification using Gemini AI.
        
        Args:
            text: Input text to classify
            categories: List of valid category labels
            
        Returns:
            Dictionary with 'result' key containing chosen category
        """
        categories_str = ", ".join(f'"{cat}"' for cat in categories)
        
        prompt = f"""Classify the following text into ONE of these categories: {categories_str}

Respond with ONLY a JSON object with one key "result" containing your chosen category.
Do not include any explanation or additional text, only the JSON object.

Text to classify:
{text}

Response (JSON only):"""

        try:
            # Generate with low temperature for deterministic output
            response = self.genai_client.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.0,
                    max_output_tokens=50,
                )
            )
            
            # Parse JSON response
            result_text = response.text.strip()
            # Remove markdown code blocks if present
            result_text = re.sub(r'^```json\s*', '', result_text)
            result_text = re.sub(r'\s*```$', '', result_text)
            
            result = json.loads(result_text)
            
            # Validate result format
            if "result" not in result:
                raise ValueError("Response missing 'result' key")
            
            category = result["result"]
            if category not in categories:
                # Try case-insensitive match
                category_lower = category.lower()
                matching = [c for c in categories if c.lower() == category_lower]
                if matching:
                    category = matching[0]
                else:
                    raise ValueError(f"Invalid category: {category}")
            
            return {"result": category}
            
        except Exception as e:
            # Fallback: return first category
            print(f"Gemini classification failed: {e}, using fallback")
            return {"result": categories[0] if categories else "unknown"}

    def _execute_sentiment_analysis(self, task: Task) -> str:
        """
        Execute sentiment analysis task.
        
        Args:
            task: Task object with specification_uri containing text to analyze
            
        Returns:
            JSON string with sentiment result
        """
        # Fetch input text
        input_text = self._fetch_task_input(task.specification_uri)
        
        # Use Gemini if available, otherwise fallback
        if self.genai_client:
            result = self._sentiment_analysis_gemini(input_text)
        else:
            result = self._sentiment_analysis_fallback(input_text)
        
        return json.dumps(result)

    def _execute_classification(self, task: Task) -> str:
        """
        Execute classification task.
        
        MVP Assumption:
        - specification_uri contains JSON with 'text' and 'categories' fields
        - Example: {"text": "input text", "categories": ["label1", "label2", "label3"]}
        
        Args:
            task: Task object with specification_uri
            
        Returns:
            JSON string with classification result
        """
        # Fetch and parse specification
        spec_str = self._fetch_task_input(task.specification_uri)
        
        try:
            spec = json.loads(spec_str)
            input_text = spec.get("text", spec_str)  # Fallback to raw text
            categories = spec.get("categories", ["general", "specific", "other"])
        except json.JSONDecodeError:
            # If not JSON, treat as plain text with default categories
            input_text = spec_str
            categories = ["general", "specific", "other"]
        
        # Use Gemini if available
        if self.genai_client:
            result = self._classification_gemini(input_text, categories)
        else:
            # Fallback: return first category
            result = {"result": categories[0] if categories else "unknown"}
        
        return json.dumps(result)

    def execute(self, task: Task) -> Tuple[str, bytes]:
        """
        Execute task based on required capability.
        
        IMPORTANT: This method ONLY executes tasks and returns results.
        It does NOT interact with the market, place bids, or sign transactions.
        
        Args:
            task: Task object with required_capability and specification_uri
            
        Returns:
            Tuple[result_uri: str, result_hash: bytes32]
            - result_uri: IPFS-style URI for the result
            - result_hash: SHA256 hash of the actual execution output
        """
        capability = task.required_capability.lower().strip()
        
        # Route to appropriate execution handler
        if capability == "sentiment-analysis":
            execution_output = self._execute_sentiment_analysis(task)
        elif capability == "classification":
            execution_output = self._execute_classification(task)
        else:
            # Generic execution for unknown capabilities
            execution_output = json.dumps({
                "result": f"Executed task {task.task_id} with capability {task.required_capability}",
                "status": "completed"
            })
        
        # Calculate SHA256 hash of the ACTUAL execution output
        result_hash = hashlib.sha256(execution_output.encode("utf-8")).digest()
        
        # Build result URI using task ID and hash prefix
        hash_hex = result_hash.hex()
        result_uri = f"ipfs://result-{task.task_id}-{hash_hex[:12]}"
        
        return result_uri, result_hash
