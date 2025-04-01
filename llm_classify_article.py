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
    from prompts.user_prompt import (
        USER_CRITERIA,
        direct_classify_prompt,
        cot_pre_answer,
        COT_CONFIRM,
        COT_PREFILL,
        PREFILL,
    )

except ModuleNotFoundError:
    # Fallback to sample prompts with warning
    warnings.warn(
        "Using sample prompts - Create prompts/user_prompt.py with your own criteria",
        UserWarning,
    )
    from prompts.sample_user_prompt import (
        USER_CRITERIA,
        direct_classify_prompt,
        cot_pre_answer,
        COT_CONFIRM,
        COT_PREFILL,
        PREFILL,
    )


def classify_article_relevance(title, abstract, use_cot=False):
    """Classify article relevance using LLM. Returns LLM response"""
    print(f"\nClassifying: {title[:80]}...")  # Truncate very long titles
    if not (use_cot):
        formatted_prompt = direct_classify_prompt.format(
            user_criteria=USER_CRITERIA, title=title, abstract=abstract
        )
        messages = [
            {"role": "system", "content": ""},
            {"role": "user", "content": formatted_prompt},
            {"role": "assistant", "content": PREFILL},
        ]
        message, first_token, first_logprob, first_prob = get_llm_response(
            messages, logprobs=True, top_logprobs=5, temperature=0
        )
    else:
        cot_prep_prompt = cot_pre_answer.format(
            user_criteria=USER_CRITERIA, title=title, abstract=abstract
        )
        messages = [
            {"role": "system", "content": ""},
            {"role": "user", "content": cot_prep_prompt},
        ]
        cot_message, first_token, first_logprob, first_prob = get_llm_response(
            messages, temperature=0
        )
        print(f"COT: {cot_message}")
        messages += [
            {"role": "assistant", "content": cot_message},
            {"role": "user", "content": COT_CONFIRM},
            {"role": "assistant", "content": COT_PREFILL},
        ]
        message, first_token, first_logprob, first_prob = get_llm_response(
            messages, logprobs=True, top_logprobs=5, temperature=0
        )

    # print(f"LLM classification: '{message.strip()}'")
    # print(first_token, first_logprob, first_prob)
    return message.strip(), first_prob


# Example usage
if __name__ == "__main__":
    sample_title = "Climate Change Impacts on Coastal Ecosystems"
    sample_abstract = (
        "This study examines temperature-driven changes in marine biodiversity..."
    )

    print("\n=== Example Classification ===")
    result, prob = classify_article_relevance(sample_title, sample_abstract)
    print(f"Final decision: {result} {prob}%")
    print()

    print("\n=== Example Classification with COT===")
    result, prob = classify_article_relevance(sample_title, sample_abstract, use_cot=True)
    print(f"Final decision: {result} {prob}%")
    print("=" * 30)
