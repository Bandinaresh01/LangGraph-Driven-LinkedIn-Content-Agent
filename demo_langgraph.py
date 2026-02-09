from typing import TypedDict, Literal
import os
from dotenv import load_dotenv

from langgraph.graph import StateGraph, END
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI


load_dotenv()

@tool
def myprevious_data_post() -> str:
    """Return my background info to personalize the LinkedIn caption."""
    return (
        "My name is Naresh. I’m a final-year B.Tech student at Vardhaman College of Engineering "
        "in the AIML branch. I’m passionate about AI and applying it to real-world problems that "
        "create scalable, real value. I love learning why/how things work—both technical and non-technical."
    )


class State(TypedDict):
    topic: str
    post: str
    review: str
    tries: int


def config_llm():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in environment")
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.2,
        api_key=api_key,
    )
    # ✅ correct tool binding
    llm = llm.bind_tools([myprevious_data_post])
    return llm


def generate_caption(state: State):
    llm = config_llm()
    sys_msg = os.getenv("GEN_CAPTION_SYSTEM", "You write strong LinkedIn captions.")
    prompt = ChatPromptTemplate.from_messages([
        ("system", sys_msg),
        ("human", "Write a LinkedIn caption for this topic: {topic}. "
                  "Use my background if useful via tools.")
    ])
    chain = prompt | llm | StrOutputParser()
    post = chain.invoke({"topic": state["topic"]})
    print(post)
    return {"post": post}


def review_caption(state: State):
    llm = config_llm()
    sys_msg = os.getenv("REVIEW_CAP_SYSTEM", "You are a strict LinkedIn post reviewer.")
    prompt = ChatPromptTemplate.from_messages([
        ("system", sys_msg),
        ("human", "Review this LinkedIn post. If no changes are needed reply ONLY 'yes'. "
                  "Otherwise reply ONLY 'comments' and then give bullet-point improvements.\n\nPOST:\n{post}")
    ])
    chain = prompt | llm | StrOutputParser()
    review = chain.invoke({"post": state["post"]})
    print(review)
    return {"post": new_post, "tries": state.get("tries", 0) + 1}



def regenerate_caption(state: State):
    llm = config_llm()
    sys_msg = os.getenv("REGENERATE_SYSTEM", "You rewrite posts based on review comments.")
    prompt = ChatPromptTemplate.from_messages([
        ("system", sys_msg),
        ("human", "Rewrite the post using these review notes.\n\nPOST:\n{post}\n\nREVIEW:\n{review}")
    ])
    chain = prompt | llm | StrOutputParser()
    new_post = chain.invoke({"post": state["post"], "review": state["review"]})
    return {"post": new_post}


def route_after_review(state):
    if state.get("tries", 0) >= 2:
        return "yes"   # force stop after 2 regenerations
    return "yes" if state["review"].strip().lower().startswith("yes") else "comments"


graph = StateGraph(State)
graph.add_node("generate_caption", generate_caption)
graph.add_node("review_caption", review_caption)
graph.add_node("regenerate_caption", regenerate_caption)

graph.set_entry_point("generate_caption")
graph.add_edge("generate_caption", "review_caption")

graph.add_conditional_edges(
    "review_caption",
    route_after_review,
    {
        "yes": END,
        "comments": "regenerate_caption",
    }
)

graph.add_edge("regenerate_caption", "review_caption")

app = graph.compile()

result = app.invoke({"topic": "How I built my first LangGraph workflow", "post": "", "review": ""})
print(result["post"])
print("Review:", result["review"])
