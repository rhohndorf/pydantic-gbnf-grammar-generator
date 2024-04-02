from enum import Enum
import json
from typing import Optional, List

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

# A example structured output based on pydantic models. The LLM will create an entry for a Book database out of an unstructured text.
class Category(Enum):
    """
    The category of the book.
    """
    Fiction = "Fiction"
    NonFiction = "Non-Fiction"


class Book(BaseModel):
    """
    Represents an entry about a book.
    """
    title: str = Field(..., description="Title of the book.")
    author: str = Field(..., description="Author of the book.")
    published_year: Optional[int] = Field(..., description="Publishing year of the book.")
    keywords: List[str] = Field(..., description="A list of keywords.")
    category: Category = Field(..., description="Category of the book.")
    summary: str = Field(..., description="Summary of the book.")


# We need no additional parameters other than our list of pydantic models.
gbnf_grammar, documentation = generate_gbnf_grammar_and_documentation([Book])
print(gbnf_grammar)

system_message = "You are an advanced AI, tasked to create a dataset entry in JSON for a Book. The following is the expected output model:\n\n" + documentation

text = """The Feynman Lectures on Physics is a physics textbook based on some lectures by Richard Feynman, a Nobel laureate who has sometimes been called "The Great Explainer". The lectures were presented before undergraduate students at the California Institute of Technology (Caltech), during 1961–1963. The book's co-authors are Feynman, Robert B. Leighton, and Matthew Sands."""
prompt = f"<|im_start|>system\n{system_message}<|im_end|>\n<|im_start|>user\n{text}<|im_end|>\n<|im_start|>assistant"

text = create_completion(prompt=prompt, grammar=gbnf_grammar)

json_data = json.loads(text)

print(Book(**json_data))

