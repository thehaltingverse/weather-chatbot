import os
import sys
from typing import List, Dict, Optional
from dotenv import load_dotenv

# Load .env variables
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "env", ".env")
load_dotenv(dotenv_path=env_path)

# Attempt to load OpenAI key
# Recommend NOT switching to local model due to slow interaction speeds and less robust responses.
OPENAI_API_KEY = os.getenv("OPENAI_KEY_BACKUP")

# Import new OpenAI client if installed
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

# Define constants
SYSTEM_PROMPT = """
You are a professional and friendly CLI assistant helping a user get a 7-day weather forecast. Your only job is to obtain a valid U.S. location in the format "City, ST" (e.g., "Austin, TX") from the user.

IMPORTANT CONSTRAINTS:
- The location must be in the United States and must contain a USW (NOAA weather station) nearby.
- The required format is: "City, ST" (capitalized state abbreviation).
- You have a maximum of 5 turns TOTAL to get a valid location.
- If the user does not provide a valid location within 5 turns, politely explain the app will close.
- You must stay within scope. Do not answer any unrelated questions, but instead gently direct them back to providing a location for a weather forecast.

DIALOGUE BEHAVIOR:
- Start by clearly stating the goal and limitations of this chat.
- On each user turn, validate the input:
    - If the input looks malformed (wrong format), explain and re-prompt with an example.
    - If the city is unknown or likely invalid (e.g., made up), express uncertainty and ask for a better-known U.S. city.
    - If there is ambiguity, for example, "Portland" input, but unclear if "Portland, OR" or "Portland, ME", ask for clarification based on what you suspect.
- Be friendly but professional in tone.
- NEVER provide weather data yourself — just collect and validate the location.

Once a valid location is received, respond with the below and :
"Thank you! I’ve received a valid location: {location}"

If 10 turns pass without a valid input, say:
"Unfortunately, I wasn't able to get a valid U.S. city and state from you in the required format within 10 turns. Please restart the app and try again. Goodbye!"
"""

# --- Option 1: Use OpenAI GPT ---
def run_openai_chat(model="gpt-4o-mini", max_turns=10) -> Optional[str]:
    if OpenAI is None:
        print("❌ OpenAI Python SDK >=1.0.0 is required for this mode.")
        sys.exit(1)
    
    client = OpenAI(api_key=OPENAI_API_KEY)

    messages: List[Dict[str, str]] = [{"role": "system", "content": SYSTEM_PROMPT}]
    turn = 0

    print("🤖 Running assistant via OpenAI...\n")

    while turn < max_turns:
        if turn == 0:
            response = client.chat.completions.create(model=model, messages=messages)
            assistant_reply = response.choices[0].message.content
            print(f"\nAssistant: {assistant_reply}")
            messages.append({"role": "assistant", "content": assistant_reply})

        user_input = input("\nYou: ").strip()
        messages.append({"role": "user", "content": user_input})

        response = client.chat.completions.create(model=model, messages=messages)
        assistant_reply = response.choices[0].message.content
        print(f"\nAssistant: {assistant_reply}")
        messages.append({"role": "assistant", "content": assistant_reply})

        if "Thank you! I’ve received a valid location:" in assistant_reply:
            
            return assistant_reply.split("location:")[-1].split(".")[0].strip()

        turn += 1

    print("\nUnfortunately, I wasn't able to get a valid location in time. Goodbye!")
    return None


# --- Option 2: Use local LLM via llama-cpp-python ---
def run_local_chat(model_path="models/openchat-3.5-1210.Q4_K_M.gguf", max_turns=10) -> Optional[str]:
    from llama_cpp import Llama

    print("🤖 Running assistant via local model...\n")

    llm = Llama(
        model_path=model_path,
        chat_format="chatml",  # works well with OpenChat; can be adjusted
        n_ctx=2048,
        temperature=0.7,
        top_p=0.95,
        stop=["</s>"],
        verbose=False
    )

    messages: List[Dict[str, str]] = [{"role": "system", "content": SYSTEM_PROMPT}]
    turn = 0

    while turn < max_turns:
        if turn == 0:
            assistant_reply = llm.create_chat_completion(messages)["choices"][0]["message"]["content"]
            print(f"\nAssistant: {assistant_reply}")
            messages.append({"role": "assistant", "content": assistant_reply})

        user_input = input("\nYou: ").strip()
        messages.append({"role": "user", "content": user_input})

        assistant_reply = llm.create_chat_completion(messages)["choices"][0]["message"]["content"]
        print(f"\nAssistant: {assistant_reply}")
        messages.append({"role": "assistant", "content": assistant_reply})

        if "Thank you! I’ve received a valid location:" in assistant_reply:
            return assistant_reply.split("location:")[-1].split(".")[0].strip()

        turn += 1

    print("\nUnfortunately, I wasn't able to get a valid location in time. Goodbye!")
    return None


# --- Main selector ---
def run_location_chat(max_turns=5) -> Optional[str]:
    if OPENAI_API_KEY:
        return run_openai_chat(max_turns=max_turns)
    else:
        local_model_path = "models/openchat-3.5-1210.Q4_K_M.gguf"
        if not os.path.exists(local_model_path):
            print(f"❌ Local model not found at {local_model_path}.")
            print("Please download the GGUF file or set your OpenAI API key in the .env file.")
            sys.exit(1)
        return run_local_chat(model_path=local_model_path, max_turns=max_turns)
