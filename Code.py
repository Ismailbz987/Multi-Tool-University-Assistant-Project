from openai import OpenAI, OpenAIError
from dotenv import load_dotenv
import requests
import json
import os

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("API key is mising!")
client = OpenAI(api_key = api_key)
def get_github_user(username):
    response = requests.get(
        "https://api.github.com/users/" + username,
        timeout = 10
            
    )
    response.raise_for_status()
    data = response.json()
    return  {
        "username" : data["login"],
        "followers" : data["followers"],
    }
tools = [
    {
        "type" : "function",
        "name" : "get_github_user",
        "description" : "get user information from github",
        "parameters" : {
            "type" : "object",
            "properties" : {
                "username" : {
                    "type" : "string"
                }
            },
            "required" : ["username"],
            "additionalProperties" : False
        },
        "strict" : True
    }
]
question = input("You: ")
try:
    response = client.responses.create(
    model = "gpt-4.1-mini",
    input = question,
    tools = tools,
    tool_choice = "required"
)
    for item in response.output:
        if item.type == "function_call":
            print("Function requested: ", item.name)
            print("Arguments: ", item.arguments)
            arguments = json.loads(item.arguments)
            if item.name == "get_github_user":
                username = arguments["username"]
                result = get_github_user(username)
                print("Function result:", result)
                final_response = client.responses.create(
                    model="gpt-4.1-mini",
                    previous_response_id = response.id,
                    input = 
                        [{
                            "type" : "function_call_output",
                            "call_id" : item.call_id,
                            "output" : json.dumps(result)
                        }],
                tools = tools,
                tool_choice = "none"

                )
                print("\nAI answer: ", final_response.output_text) # we move this inside, because  if we move it outside the "if" condition,  the model might returns a different function call, then final_response might not exist yet.

except OpenAIError as e:
    print("API request failed!")
    print("Error: ", e)

except json.JSONDecodeError as e:
    print("The function arguments were not valid!")
    print("Error: ", e)

except KeyError as e:
    print("A required function argument is missing!")
    print("Error: ", e)

except requets.RequestException as e:
    print("GitHub API request failed!")
    print("Error: ", e)


