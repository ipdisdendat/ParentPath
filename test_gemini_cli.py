"""Test Gemini CLI mode implementation"""
import asyncio
import os
from api.services.gemini_service import _execute_via_cli, USE_CLI
from api.config import settings


async def test_cli_mode():
    """Test basic CLI execution"""

    print(f"USE_CLI: {USE_CLI}")
    print(f"API Key configured: {bool(settings.gemini_api_key)}")

    if not settings.gemini_api_key:
        print("SKIP: No GEMINI_API_KEY set in environment")
        return

    if not USE_CLI:
        print("SKIP: use_gemini_cli=False in config")
        return

    # Test simple text-only prompt
    try:
        print("\nTesting simple text prompt...")
        response = await _execute_via_cli("What is 2+2? Answer with just the number.")
        print(f"Response: {response}")
        assert "4" in response, "Expected '4' in response"
        print("✓ Text-only CLI test passed")

    except Exception as e:
        print(f"✗ CLI test failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(test_cli_mode())
