"""Gemini AI service for multimodal parsing, embeddings, and translation"""
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import json
import logging
import subprocess
import base64
from typing import List, Dict, Any, Optional
from pathlib import Path

from api.config import settings

logger = logging.getLogger(__name__)

# Determine execution mode
USE_CLI = settings.use_gemini_cli

# Configure Gemini API (only if not using CLI)
if not USE_CLI:
    genai.configure(api_key=settings.gemini_api_key)

    # Create model instance
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash-exp",
        safety_settings={
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        },
        generation_config={
            "temperature": 0.1,  # Low for consistent extraction
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
        }
    )


async def _execute_via_cli(prompt: str, file_path: Optional[str] = None, model_name: str = "gemini-2.0-flash-exp") -> str:
    """
    Execute Gemini request via curl to REST API (free tier compatible)

    Args:
        prompt: Text prompt for Gemini
        file_path: Optional file path for multimodal input
        model_name: Gemini model to use

    Returns:
        Response text from Gemini
    """
    try:
        # Build request body
        parts = []

        # Add file if provided (encode as base64 inline data)
        if file_path:
            with open(file_path, 'rb') as f:
                file_data = base64.b64encode(f.read()).decode('utf-8')

            # Determine MIME type
            suffix = Path(file_path).suffix.lower()
            mime_map = {
                '.pdf': 'application/pdf',
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
            }
            mime_type = mime_map.get(suffix, 'application/octet-stream')

            parts.append({
                "inline_data": {
                    "mime_type": mime_type,
                    "data": file_data
                }
            })

        # Add text prompt
        parts.append({"text": prompt})

        # Build request payload
        request_body = {
            "contents": [{"parts": parts}],
            "generationConfig": {
                "temperature": 0.1,
                "topP": 0.95,
                "topK": 40,
                "maxOutputTokens": 8192,
            },
            "safetySettings": [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
            ]
        }

        # Execute curl request
        cmd = [
            "curl", "-X", "POST",
            f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={settings.gemini_api_key}",
            "-H", "Content-Type: application/json",
            "-d", json.dumps(request_body)
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

        if result.returncode != 0:
            raise RuntimeError(f"Curl command failed: {result.stderr}")

        # Parse response
        response_data = json.loads(result.stdout)

        # Extract text from response
        if "candidates" in response_data and len(response_data["candidates"]) > 0:
            candidate = response_data["candidates"][0]
            if "content" in candidate and "parts" in candidate["content"]:
                parts = candidate["content"]["parts"]
                if len(parts) > 0 and "text" in parts[0]:
                    return parts[0]["text"]

        # Fallback error handling
        if "error" in response_data:
            raise RuntimeError(f"Gemini API error: {response_data['error']}")

        raise RuntimeError(f"Unexpected response structure: {response_data}")

    except subprocess.TimeoutExpired:
        logger.error("Gemini CLI request timed out")
        raise RuntimeError("Gemini request timed out after 60 seconds")
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse Gemini CLI response: {e}")
        logger.error(f"Response stdout: {result.stdout}")
        raise RuntimeError(f"Invalid JSON response from Gemini CLI: {e}")
    except Exception as e:
        logger.error(f"Error executing Gemini via CLI: {e}")
        raise


async def parse_pdf_newsletter(file_path: str) -> List[Dict[str, Any]]:
    """
    Parse PDF newsletter using Gemini multimodal API

    Args:
        file_path: Path to PDF file

    Returns:
        List of extracted items with confidence scores
    """
    try:
        logger.info(f"Parsing PDF newsletter: {file_path} (mode: {'CLI' if USE_CLI else 'API'})")

        # Structured extraction prompt
        prompt = """
Extract all events, announcements, permission slips, and deadlines from this school newsletter.

For each item, extract:
- type: One of ["Event", "PermissionSlip", "Fundraiser", "HotLunch", "Announcement"]
- title: string (required)
- description: string (optional, brief summary)
- date: YYYY-MM-DD format (required if type=Event or has deadline)
- time: HH:MM format in 24-hour (optional)
- end_date: YYYY-MM-DD (for multi-day events, optional)
- location: string (optional)
- audience_tags: array of strings (required, at least ["all"])
  * Use "grade_X" for grade-specific items (e.g., "grade_5")
  * Use activity names for activity-specific (e.g., "Basketball", "Band")
  * Use "all" for school-wide announcements
- action_link: URL if there's a sign-up/payment link (optional)
- deadline: YYYY-MM-DD HH:MM for permission slips, registrations (optional)
- cost: decimal number if money required (optional)
- source_page: integer page number in PDF (required)
- source_snippet: exact 1-2 sentence excerpt from newsletter (required)

Also provide per-item:
- confidence_score: 0.0-1.0 for extraction confidence
- reasoning: explanation if confidence < 0.9

Return ONLY a valid JSON array of items. No markdown, no commentary.
Example:
[
  {
    "type": "Event",
    "title": "Basketball practice",
    "description": "Weekly practice session",
    "date": "2024-11-20",
    "time": "16:00",
    "location": "School gym",
    "audience_tags": ["grade_5", "Basketball"],
    "source_page": 3,
    "source_snippet": "Basketball practice for Grade 5 on Nov 20 at 4pm in the gym.",
    "confidence_score": 0.95,
    "reasoning": ""
  }
]

Be thorough - extract EVERYTHING. If uncertain about a field, include it with lower confidence.
"""

        # Execute via CLI or API
        if USE_CLI:
            response_text = await _execute_via_cli(prompt, file_path)
        else:
            # Upload file to Gemini
            uploaded_file = genai.upload_file(file_path)
            # Generate response
            response = model.generate_content([uploaded_file, prompt])
            response_text = response.text.strip()

        # Remove markdown code blocks if present
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
            response_text = response_text.strip()

        items_data = json.loads(response_text)

        logger.info(f"Extracted {len(items_data)} items from newsletter")

        return items_data

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse Gemini response as JSON: {e}")
        logger.error(f"Response text: {response.text}")
        raise ValueError(f"Invalid JSON response from Gemini: {e}")
    except Exception as e:
        logger.error(f"Error parsing PDF newsletter: {e}")
        raise


async def parse_image_flyer(image_path: str) -> Dict[str, Any]:
    """
    Parse scanned flyer or parent-submitted photo

    Args:
        image_path: Path to image file

    Returns:
        Extracted item dict with confidence score
    """
    try:
        logger.info(f"Parsing image flyer: {image_path} (mode: {'CLI' if USE_CLI else 'API'})")

        prompt = """
This is a photo of a school flyer or permission slip.

Extract:
- type: What kind of item is this? (Event, PermissionSlip, Fundraiser, etc.)
- title: The headline/title
- description: Brief description of what this is about
- date: When is this event/deadline? (YYYY-MM-DD format)
- time: What time? (HH:MM 24-hour format)
- location: Where is this happening?
- audience_tags: Who is this for? (grades, activities, or "all")
- deadline: Any deadline mentioned? (YYYY-MM-DD HH:MM)
- cost: Any cost mentioned?
- source_snippet: Transcribe the key information from the image

Notes:
- If the image is blurry: set confidence < 0.7 and note in reasoning
- If partially cut off: extract what's visible, note limitation in reasoning
- If upside down or rotated: correct and extract normally

Return a single JSON object (not an array):
{
  "type": "Event",
  "title": "...",
  ...
  "confidence_score": 0.85,
  "reasoning": "Image slightly blurry on right side"
}
"""

        # Execute via CLI or API
        if USE_CLI:
            response_text = await _execute_via_cli(prompt, image_path)
        else:
            # Upload image to Gemini
            uploaded_file = genai.upload_file(image_path)
            response = model.generate_content([uploaded_file, prompt])
            response_text = response.text.strip()

        # Parse JSON - remove markdown code blocks if present
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
            response_text = response_text.strip()

        item_data = json.loads(response_text)

        logger.info(f"Extracted item from image: {item_data.get('title')}")

        return item_data

    except Exception as e:
        logger.error(f"Error parsing image flyer: {e}")
        raise


async def generate_embedding(text: str) -> List[float]:
    """
    Generate 768-dimensional embedding for Qdrant

    Args:
        text: Text to embed

    Returns:
        List of float values (768-dim vector)
    """
    try:
        if USE_CLI:
            # Use REST API for embeddings
            request_body = {
                "model": "models/text-embedding-004",
                "content": {
                    "parts": [{"text": text}]
                },
                "taskType": "RETRIEVAL_DOCUMENT"
            }

            cmd = [
                "curl", "-X", "POST",
                f"https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:embedContent?key={settings.gemini_api_key}",
                "-H", "Content-Type: application/json",
                "-d", json.dumps(request_body)
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode != 0:
                raise RuntimeError(f"Curl command failed: {result.stderr}")

            response_data = json.loads(result.stdout)

            if "embedding" in response_data and "values" in response_data["embedding"]:
                return response_data["embedding"]["values"]

            raise RuntimeError(f"Unexpected embedding response: {response_data}")

        else:
            # Use API mode
            result = genai.embed_content(
                model="models/text-embedding-004",
                content=text,
                task_type="retrieval_document"
            )

            return result['embedding']

    except Exception as e:
        logger.error(f"Error generating embedding: {e}")
        raise


async def translate_text(text: str, target_language: str) -> str:
    """
    Translate text to target language

    Args:
        text: Text to translate
        target_language: ISO 639-1 code (en, pa, tl, zh, es)

    Returns:
        Translated text
    """
    LANGUAGE_MAP = {
        "en": "English",
        "pa": "Punjabi (Gurmukhi script)",
        "tl": "Tagalog",
        "zh": "Simplified Chinese",
        "es": "Spanish"
    }

    if target_language == "en":
        return text  # No translation needed

    try:
        target_lang_name = LANGUAGE_MAP.get(target_language, target_language)

        prompt = f"""
Translate this school digest to {target_lang_name}.

Preserve:
- Emoji and formatting (keep line breaks)
- URLs (don't translate)
- Dates and times (adapt format to locale if appropriate)
- Grade numbers (e.g., "Grade 5" → appropriate in target language)
- Activity names (keep in English or translate if natural)

Tone: Friendly, clear, concise - appropriate for parents.

Content to translate:
{text}

Return ONLY the translated text, nothing else.
"""

        # Execute via CLI or API
        if USE_CLI:
            response_text = await _execute_via_cli(prompt)
        else:
            response = model.generate_content(prompt)
            response_text = response.text.strip()

        return response_text

    except Exception as e:
        logger.error(f"Error translating text to {target_language}: {e}")
        return text  # Fallback to original text


async def generate_answer(query: str, context_items: List[Dict[str, Any]]) -> str:
    """
    Generate natural language answer based on query and context

    Args:
        query: Parent's question
        context_items: Relevant items from Qdrant search

    Returns:
        Natural language answer
    """
    try:
        # Build context string
        context = "\n".join([
            f"- {item.get('title')} on {item.get('date')}: {item.get('description', '')}"
            for item in context_items
        ])

        prompt = f"""
Parent asked: "{query}"

Relevant school information:
{context}

Provide a helpful, concise response (2-3 sentences max).
Include date/time if relevant.
End with "Reply DONE if this helps, or ask another question."

Be friendly and conversational, like a helpful neighbor.
"""

        # Execute via CLI or API
        if USE_CLI:
            response_text = await _execute_via_cli(prompt)
        else:
            response = model.generate_content(prompt)
            response_text = response.text.strip()

        return response_text

    except Exception as e:
        logger.error(f"Error generating answer: {e}")
        return "I couldn't find an answer to your question. Try asking differently or reply HELP for options."
