# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "openai",
#     "numpy",
# ]
# ///

from llm_interface import get_llm_response
import warnings

try:
    # Attempt to import user-specific prompts
    from prompts.user_prompt import USER_CRITERIA, CLASSIFY_PROMPT, PREFILL
except ModuleNotFoundError:
    # Fallback to sample prompts with warning
    warnings.warn("Using sample prompts - Create prompts/user_prompt.py with your own criteria", UserWarning)
    from prompts.sample_user_prompt import USER_CRITERIA, CLASSIFY_PROMPT, PREFILL


def classify_article_relevance(title, abstract):
    """Classify article relevance using LLM. Returns 'Yes', 'No' or 'n.a.'"""
    formatted_prompt = CLASSIFY_PROMPT.format(
        user_criteria=USER_CRITERIA,
        title=title,
        abstract=abstract
    )
    print(f"\nClassifying: {title[:80]}...")  # Truncate very long titles
    message, first_token, first_logprob, first_prob = get_llm_response(formatted_prompt, prefill=PREFILL, logprobs=True, top_logprobs=5, temperature=0)
    # print(f"LLM classification: '{message.strip()}'")
    # print(first_token, first_logprob, first_prob)
    return message.strip(), first_prob

# Example usage
if __name__ == "__main__":
    sample_title = "Climate Change Impacts on Coastal Ecosystems"
    sample_abstract = "This study examines temperature-driven changes in marine biodiversity..."
    
    print("\n=== Example Classification ===")
    result, prob = classify_article_relevance(sample_title, sample_abstract)
    print(f"Final decision: [{result}] {prob}%")
    print("="*30)
