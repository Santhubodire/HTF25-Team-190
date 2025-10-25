import os
from dotenv import load_dotenv
from openai import OpenAI
load_dotenv() # Load environment variables from .env file
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_code(command):
    """Generate Python code from natural language command."""
    prompt = f"Generate Python code for the following command: {command}"
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful coding assistant."},
            {"role": "user", "content": prompt}
        ]
    )

    code_output = response.choices[0].message.content
    return code_output
