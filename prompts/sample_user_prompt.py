USER_CRITERIA = """Using remote sensing and machine learning to monitor or predict the impact of urbanization on air quality. Air quality can be assessed using various pollutants such as PM2.5, NOx, and O3. Any scientific articles that may provide information on dataset sources can be relevant.
Factors of impact on air quality:
- climate
- industrial activity
- transportation patterns
- green space distribution
- population density
Area of study: urban areas in temperate climates"""

direct_classify_prompt = """Determine if this academic article might be relevant based on the user's research interests. Consider the title and abstract. Reply ONLY with:
- "Yes" if clearly relevant
- "No" if not relevant

User's research focus: {user_criteria}

Article Title: {title}
Abstract Excerpt: {abstract}
"""

cot_pre_answer = """Determine if this academic article might be relevant based on the user's research interests. Consider the title and abstract. In the end, you will answer with:
- "Yes" if clearly relevant
- "No" if not relevant

User's research focus: {user_criteria}

Article Title: {title}
Abstract Excerpt: {abstract}

Think carefully of the user's research focus. Try to make a short list of what would be related to the research focus.
Then, check the article's title and abstract and try to argue how it is related or not to the research focus.
"""

COT_CONFIRM = """OK, now let's do a confirmation of your answer, reply with only "Yes" or "No" in a box based on your previous reasoning."""

COT_PREFILL = r"""Certainly, based on the reasoning above, the answer is: \boxed{"""

PREFILL = r"""Sure, I will answer with just "Yes" or "No" regarding the relevance of the article with your research focus. My answer is: \boxed{"""