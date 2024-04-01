from enum import Enum
import json
from typing import Union

from pydantic import BaseModel, Field
import requests

from pydantic_gbnf_grammar_generator import generate_gbnf_grammar_and_documentation


# Function to get completion on the llama.cpp server with grammar.
def create_completion(prompt, grammar):
    headers = {"Content-Type": "application/json"}
    data = {"prompt": prompt, "grammar": grammar, "stop": ["<|im_end|>"]}

    response = requests.post("http://127.0.0.1:8080/completion", headers=headers, json=data)
    data = response.json()

    print(data["content"])
    return data["content"]


# A function for the agent to send a message to the user.
class SendMessageToUser(BaseModel):
    """
    Send a message to the User.
    """

    chain_of_thought: str = Field(..., description="Your chain of thought while sending the message.")
    message: str = Field(..., description="Message you want to send to the user.")

    def run(self):
        print(self.message)


# Enum for the calculator tool.
class MathOperation(Enum):
    ADD = "add"
    SUBTRACT = "subtract"
    MULTIPLY = "multiply"
    DIVIDE = "divide"


# Simple pydantic calculator tool for the agent that can add, subtract, multiply, and divide. Docstring and description of fields will be used in system prompt.
class Calculator(BaseModel):
    """
    Perform a math operation on two numbers.
    """

    number_one: Union[int, float] = Field(..., description="First number.")
    operation: MathOperation = Field(..., description="Math operation to perform.")
    number_two: Union[int, float] = Field(..., description="Second number.")

    def run(self):
        if self.operation == MathOperation.ADD:
            return self.number_one + self.number_two
        elif self.operation == MathOperation.SUBTRACT:
            return self.number_one - self.number_two
        elif self.operation == MathOperation.MULTIPLY:
            return self.number_one * self.number_two
        elif self.operation == MathOperation.DIVIDE:
            return self.number_one / self.number_two
        else:
            raise ValueError("Unknown operation.")


# Here the grammar gets generated by passing the available function models to generate_gbnf_grammar_and_documentation function. This also generates a documentation usable by the LLM.
# pydantic_model_list is the list of pydanitc models
# outer_object_name is an optional name for an outer object around the actual model object. Like a "function" object with "function_parameters" which contains the actual model object. If None, no outer object will be generated
# outer_object_content is the name of outer object content.
# model_prefix is the optional prefix for models in the documentation. (Default="Output Model")
# fields_prefix is the prefix for the model fields in the documentation. (Default="Output Fields")
gbnf_grammar, documentation = generate_gbnf_grammar_and_documentation(
    pydantic_model_list=[SendMessageToUser, Calculator],
    outer_object_name="function",
    outer_object_content="function_parameters",
    model_prefix="Function",
    fields_prefix="Parameters",
)

print(gbnf_grammar)
print(documentation)

system_message = (
    "You are an advanced AI, tasked to assist the user by calling functions in JSON format. The following are the available functions and their parameters and types:\n\n"
    + documentation
)

user_message = "What is 42 * 42?"
prompt = (
    f"<|im_start|>system\n{system_message}<|im_end|>\n<|im_start|>user\n{user_message}<|im_end|>\n<|im_start|>assistant"
)

text = create_completion(prompt=prompt, grammar=gbnf_grammar)
function_dictionary = json.loads(text)
if function_dictionary["function"] == "Calculator":
    function_parameters = {**function_dictionary["function_parameters"]}

    print(Calculator(**function_parameters).run())
    # This should output: 1764