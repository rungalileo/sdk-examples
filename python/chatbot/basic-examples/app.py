import os
from galileo import openai, logger  # The Galileo OpenAI client wrapper is all you need!

from dotenv import load_dotenv ,find_dotenv

# Load environment variables
# 1) load global/shared first
load_dotenv(os.path.expanduser("~/.config/secrets/myapps.env"), override=False)
# 2) then load per-app .env (if present) to override selectively
load_dotenv(find_dotenv(usecwd=True), override=True)

client = openai.OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
    organization=os.environ.get("OPENAI_ORGANIZATION"),
)

prompt = f"Explain the following topic succinctly: Newton's First Law"
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "system", "content": prompt}],
)

print(response.choices[0].message.content.strip())
