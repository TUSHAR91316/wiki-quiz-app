# LangChain Prompt Templates

## Quiz Generation Prompt
Used in `backend/ai_generator.py` to generate the quiz content.

```text
You are an expert educator and quiz creator. Based on the following article text, create a comprehensive quiz.

Article content:
{text}

Requirements:
1. Generate 5-10 multiple-choice questions.
2. Each question must have 4 options, one correct answer, a difficulty level, and an explanation.
3. Extract key entities (people, organizations, locations).
4. Identify main sections found in the text.
5. Suggest related Wikipedia topics.
6. Ensure the output is valid JSON matching the specified format.

{format_instructions}
```
