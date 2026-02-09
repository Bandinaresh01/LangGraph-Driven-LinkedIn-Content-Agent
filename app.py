# app.py
from typing import TypedDict
import os
from dotenv import load_dotenv

from langgraph.graph import StateGraph, END
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI


# ✅ define tool at module level (cleaner)
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
    return {"post": post}


def review_caption(state: State):
    llm = config_llm()
    sys_msg = os.getenv("REVIEW_CAP_SYSTEM", "You are a strict LinkedIn post reviewer.")
    prompt = ChatPromptTemplate.from_messages([
        ("system", sys_msg),
        ("human",
         "Review this LinkedIn post. If no changes are needed reply ONLY 'yes'. "
         "Otherwise reply ONLY 'comments' and then give bullet-point improvements.\n\nPOST:\n{post}")
    ])
    chain = prompt | llm | StrOutputParser()
    review = chain.invoke({"post": state["post"]})

    # ✅ store review in state (not post)
    # ✅ increment tries ONLY when review is comments (optional, but good)
    updated = {"review": review}
    if not review.strip().lower().startswith("yes"):
        updated["tries"] = state.get("tries", 0) + 1
    return updated


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


def route_after_review(state: State):
    # stop if max tries reached
    if state.get("tries", 0) >= 2:
        return "yes"

    text = (state.get("review") or "").strip().lower()
    return "yes" if text.startswith("yes") else "comments"


# ✅ compile once (good for Flask performance)
def build_app():
    graph = StateGraph(State)
    graph.add_node("generate_caption", generate_caption)
    graph.add_node("review_caption", review_caption)
    graph.add_node("regenerate_caption", regenerate_caption)

    graph.set_entry_point("generate_caption")
    graph.add_edge("generate_caption", "review_caption")

    graph.add_conditional_edges(
        "review_caption",
        route_after_review,
        {"yes": END, "comments": "regenerate_caption"}
    )
    graph.add_edge("regenerate_caption", "review_caption")
    return graph.compile()


# Global compiled graph (reuse across requests)
load_dotenv()
GRAPH_APP = build_app()


def llm_workflow(topic: str):
    """
    Flask-friendly wrapper:
    returns (generated_post, review_text, final_post)
    """
    result = GRAPH_APP.invoke({
        "topic": topic,
        "post": "",
        "review": "",
        "tries": 0
    })

    # result["post"] is final post
    # result["review"] is last review output
    final_post = result.get("post", "")
    last_review = result.get("review", "")

    # If you want original draft too: regenerate doesn't keep it.
    # Simplest: treat final_post as content1 and last_review as content2
    return final_post, last_review
