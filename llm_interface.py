# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "openai",
#     "numpy"
# ]
# ///
from openai import OpenAI
import numpy as np
import os

# MODEL = "accounts/fireworks/models/deepseek-v3-0324"
MODEL = "accounts/fireworks/models/llama-v3p1-405b-instruct"
# MODEL = "accounts/fireworks/models/qwen2p5-72b-instruct"

def get_llm_response(prompt, prefill=None, system_message="", **kwargs):
    """Get LLM response using Fireworks.ai's DeepSeek-v3 model.

    Args:
        prompt: The user's input prompt
        prefill: Optional assistant prefill content
        system_message: Optional system message
        **kwargs: Additional parameters to pass to the API call

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
            model=MODEL, messages=messages, **kwargs
        )

        message_content = chat_completion.choices[0].message.content
        if kwargs.get('logprobs', False):
            top_tokens = chat_completion.choices[0].logprobs.content[0].top_logprobs
            first_token = top_tokens[0].token
            first_logprob = top_tokens[0].logprob
            first_prob = np.round(np.exp(first_logprob)*100,2)
            return message_content, first_token, first_logprob, first_prob
        return message_content, None, None, None
    except Exception as e:
        raise RuntimeError(f"API request failed: {str(e)}") from e


# Example usage
if __name__ == "__main__":
    prompt="I know this doesn't make any sense. But please just answer 'yes' or 'no'."
    response = get_llm_response(
        prompt,
        logprobs=True,
        top_logprobs=2,
        temperature=0,
    )
    print("LLM Response:", response)
    response = get_llm_response(
        prompt,
        logprobs=True,
        top_logprobs=2,
        temperature=0,
    )
    print("LLM Response:", response)
    response = get_llm_response(
        prompt,
    )
    print("LLM Response:", response)
