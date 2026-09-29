from openai import OpenAI, OpenAIError
from dotenv import load_dotenv
import os
import json

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("API key is missing!")

client = OpenAI(api_key=api_key)

def get_student_grade(name):
    grades = {
        "Ismail" : 92,
        "Samir" : 74,
        "Ahmed" : 91
    }
    if name in grades:
        return {
            "name" : name,
            "grade" : grades[name]
        }
    else:
        return {
            "error" : "Student name not found!"
        }
def get_course_teacher(course):
    teachers = {
        "AI Application" : "Thomas",
        "Machine Learning" : "Wang",
        "Database" : "Omar"
    }
    if course in teachers:
        return {
            "teacher" : teachers[course],
            "course" : course
        }
    else:
        return {
            "error" : "Course Not Found!"
        }
tools = [{
    "type" : "function",
    "name" : "get_student_grade",
    "description" : "get student grade for a student.",
    "parameters" : {
        "type" : "object",
        "properties" : {
            "name" : {
                "type" : "string"
            },
        },
        "required" : ["name"],
        "additionalProperties" : False
    },
    "strict" : True

},       {
    "type" : "function",
    "name" : "get_course_teacher",
    "description" : "Get the teacher for a given course.",
    "parameters" : {
        "type" : "object",
        "properties" : {
            "course": {
                "type" : "string"
            }
        },
        "required" : ["course"],
        "additionalProperties" : False
    },
    "strict" : True
}
]

question = input("You: ")

try:
    response = client.responses.create(
        model = "gpt-5.6-luna",
        input = question,
        tools = tools,
    )
    tool_output = []
    for item in response.output:
        if item.type == "function_call":
            arguments = json.loads(item.arguments)
            if item.name == "get_student_grade":
                result = get_student_grade(arguments["name"])
            elif item.name == "get_course_teacher":
                result = get_course_teacher(arguments["course"])
            else:
                result = {
                    "error" : "Unknown tool requested"
                }
            
            tool_output.append(
                        {
                        "type" : "function_call_output",
                        "call_id" : item.call_id,
                        "output" : json.dumps(result)
                        }
            )
    if tool_output:
        final_response = client.responses.create(
            previous_response_id = response.id,
            model = "gpt-5.6-luna",
            input = tool_output,
            tools = tools,
            tool_choice = "none"
        )
        print("AI: ", final_response.output_text)    
    else:
        print("AI: ", response.output_text) # No tool was requested, so final_response only exists if a tool was actually called.
except OpenAIError as e:
    print("AI API request failed!")
    print("Error:", e)
except json.JSONDecodeError as e:
    print("The function arguments were not valid JSON!")
    print("Error:", e)
except KeyError as e:
    print("A required function argument is missing!")
    print("Error:", e)

