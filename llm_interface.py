# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "openai",
# ]
# ///
from openai import OpenAI
import os

# MODEL = "accounts/fireworks/models/deepseek-v3"
MODEL = "accounts/fireworks/models/llama-v3p1-405b-instruct"

def get_llm_response(prompt, prefill=None, system_message=""):
    """Get LLM response using Fireworks.ai's DeepSeek-v3 model.

    Raises:
        ValueError: If LLM_ environment variables are missing
        RuntimeError: For API connection errors
    """
    # Check for required CITA environment variables
    api_key = os.environ.get("LLM_API_KEY")
    base_url = os.environ.get("LLM_API_URL")

    if not api_key:
        raise ValueError(
            "LLM_API_KEY environment variable is required. "
            "Get your API key from an OpenAI-compatible platform "
            "(like Fireworks.ai) and set it using:\n"
            "export LLM_API_KEY='your-key-here'"
        )
    if not base_url:
        raise ValueError(
            "LLM_API_URL environment variable is required. "
            "Set the API base URL using:\n"
            "export LLM_API_URL='https://api.fireworks.ai/inference/v1'"
        )

    # Existing API call logic remains the same
    try:
        client = OpenAI(api_key=api_key, base_url=base_url)
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt},
        ]
        if prefill is not None:
            messages.append({"role": "assistant", "content": prefill})
        chat_completion = client.chat.completions.create(
            model=MODEL, messages=messages
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        raise RuntimeError(f"API request failed: {str(e)}") from e


# Example usage
if __name__ == "__main__":
    response = get_llm_response("Write a short inspirational quote about technology")
    print("LLM Response:", response)
