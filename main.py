import os
import argparse
import json
import sys
from dotenv import load_dotenv
from openai import OpenAI
from prompts import system_prompt
from call_function import available_functions, call_function

def main(): 
    load_dotenv()

    # Accessing `args.user_prompt`
    parser = argparse.ArgumentParser(description="CLI chatbot")
    parser.add_argument("user_prompt", type=str, help="Ask me anyhting...")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()

    api_key = os.environ.get("OPENROUTER_API_KEY")
    if api_key is None:
        raise RuntimeError("Environment variable was not found!")

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": args.user_prompt},
    ]

    for _ in range(20):
        response = client.chat.completions.create(
            model="openrouter/free",
            messages=messages,
            tools=available_functions,
        )
        if response.usage is None:
            raise RuntimeError("API request failed")
        if args.verbose:
            print(f"User prompt: {args.user_prompt}")
            print(f"Prompt tokens: {response.usage.prompt_tokens}")
            print(f"Response tokens: {response.usage.completion_tokens}")
        
        message = response.choices[0].message
        messages.append(message)
        if message.tool_calls is None:
            print(message.content)
            break
        else:
            for tool_call in message.tool_calls:
                result_message = call_function(tool_call, args.verbose)
                messages.append(result_message)
                if not result_message.get("content"):
                    raise RuntimeError("Empty function response")
                if args.verbose:
                    print(f"-> {result_message['content']}")
    else:
        print("Maximum number of iterations reached")
        sys.exit(1)
if __name__ == "__main__":
    main()
