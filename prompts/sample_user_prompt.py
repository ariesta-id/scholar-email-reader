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
- "No" if not relevant

User's research focus: {user_criteria}

Article Title: {title}
Abstract Excerpt: {abstract}
"""

PREFILL = """Sure, I will answer with just "Yes" or "No" regarding the relevance of the article with your research focus. My answer is: """