import openai
import os
import time

api_key = os.environ.get('ALTIMETER_API_KEY')

if not api_key:
    print("OPENAI_API_KEY environment variable not found!")
    exit()

openai.api_key = api_key

try:
    response = openai.Completion.create(
      engine="gpt-3.5-turbo",
      prompt="Translate the following English text to French: 'Hello, how are you?'",
      max_tokens=60
    )
    print(response.choices[0].text.strip())
    
except openai.error.RateLimitError:
    print("Rate limit exceeded. Please wait for a while before making another request.")
    # Optionally, you can add a sleep here to delay and then retry:
    # time.sleep(60)  # Sleep for 1 minute before retrying
