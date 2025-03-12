# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "openai",
# ]
# ///

from llm_interface import get_llm_response

USER_CRITERIA = """Using remote sensing and machine learning to monitor or predict the impact of urbanization on air quality. Air quality can be assessed using various pollutants such as PM2.5, NOx, and O3. Any scientific articles that may provide information on dataset sources can be relevant.
Factors of impact on air quality:
- climate
- industrial activity
- transportation patterns
- green space distribution
- population density
Area of study: urban areas in temperate climates"""

CLASSIFY_PROMPT = """Determine if this academic article might be relevant based on the user's research interests. Consider the title and abstract. Reply ONLY with:
- "Yes" if clearly relevant
- "No" if clearly irrelevants
- "n.a." if cannot determine

User's research focus: {user_criteria}

Article Title: {title}
Abstract Excerpt: {abstract}
"""

PREFILL = """Sure, I will answer with just Yes, No, or n.a. regarding the relevance of the article with your research focus. My answer is: """

def classify_article_relevance(title, abstract):
    """Classify article relevance using LLM. Returns 'Yes', 'No' or 'n.a.'"""
    formatted_prompt = CLASSIFY_PROMPT.format(
        user_criteria=USER_CRITERIA,
        title=title,
        abstract=abstract
    )
    print(f"\nClassifying: {title[:80]}...")  # Truncate very long titles
    response = get_llm_response(formatted_prompt, prefill=PREFILL)
    print(f"LLM classification: '{response.strip()}'")
    return response.strip()

# Example usage
if __name__ == "__main__":
    sample_title = "Climate Change Impacts on Coastal Ecosystems"
    sample_abstract = "This study examines temperature-driven changes in marine biodiversity..."
    
    print("\n=== Example Classification ===")
    result = classify_article_relevance(sample_title, sample_abstract)
    print(f"Final decision: [{result}]")
    print("="*30)
