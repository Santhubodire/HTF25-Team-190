import os
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_code(prompt):
    """Generates code using OpenAI API"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful programming assistant."},
                {"role": "user", "content": f"Generate Python code for: {prompt}"}
            ],
            max_tokens=300
        )

        code = response.choices[0].message.content.strip()
        return code
    except Exception as e:
        return f"Error generating code: {str(e)}"
