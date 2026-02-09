# LangGraph-Driven LinkedIn Content Agent

An agentic AI application built with LangGraph, Gemini, and Flask that generates, reviews, and refines LinkedIn captions using a controlled multi-step workflow with tool integration and conditional routing.

---

## Features

- Agentic workflow using LangGraph (stateful nodes + conditional routing)
- Generate → Review → Regenerate loop with retry control
- Tool calling for personalization (injects user background into captions)
- Flask-based web interface for easy interaction
- Copy-ready LinkedIn captions

---

## How It Works

The system is designed as a LangGraph workflow with three main nodes:

1. Generate Caption  
   - Creates a LinkedIn caption based on the given topic.

2. Review Caption  
   - Reviews the generated caption.
   - Returns:
     - "yes" → caption is approved and workflow stops.
     - "comments" → suggestions are provided and workflow continues.

3. Regenerate Caption  
   - Rewrites the caption based on review comments.

The workflow stops automatically when the caption is approved or when the maximum retry limit is reached.

---

## Tech Stack

- Python
- LangGraph
- LangChain
- Google Gemini API
- Flask
- HTML, CSS, JavaScript

---

## Project Structure

.
├── app.py                  # LangGraph workflow and LLM configuration
├── main.py                 # Flask application
├── demo_langgraph.py       # Optional local workflow testing
├── requirements.txt
└── templates/
    ├── home.html           # Topic input page
    └── index.html          # Generated and improved output page

---

## Setup Instructions

### 1. Clone the Repository

git clone https://github.com/Bandinaresh01/LangGraph-Driven-LinkedIn-Content-Agent.git  
cd LangGraph-Driven-LinkedIn-Content-Agent

---

### 2. Create and Activate Virtual Environment

Windows (PowerShell):

python -m venv env  
env\Scripts\activate

Mac / Linux:

python3 -m venv env  
source env/bin/activate

---

### 3. Install Dependencies

pip install -r requirements.txt

---

## Environment Variables

Create a `.env` file in the project root (do NOT commit this file):

GOOGLE_API_KEY=YOUR_GEMINI_API_KEY

GEN_CAPTION_SYSTEM="You are a professional LinkedIn content writer. Write clear, engaging captions in first person. Keep it 4-6 lines and avoid emojis."

REVIEW_CAP_SYSTEM="You are a strict LinkedIn post reviewer. If the post is ready with no changes, reply ONLY: yes. Otherwise reply ONLY: comments followed by bullet-point improvements. Do not rewrite the post."

REGENERATE_SYSTEM="You are a LinkedIn content editor. Rewrite the caption using the reviewer comments. Improve clarity and impact. Output ONLY the final updated caption."

Make sure `.env` is added to `.gitignore`.

---

## Run the Application

Start the Flask server:

python main.py

Open your browser and navigate to:

http://127.0.0.1:5000

---

## Usage

1. Open the home page.
2. Enter a topic such as:
   - How I built my first LangGraph workflow
   - What I learned from building an AI agent with tools
3. Click Generate.
4. Copy the improved LinkedIn caption and post it.

---

## Gemini API Rate Limits

When using the free Gemini API tier, you may encounter 429 RESOURCE_EXHAUSTED errors due to request limits.

To avoid this:
- Limit regeneration retries.
- Wait before retrying.
- Upgrade API quota if needed.

---

## Future Enhancements

- Store caption and review history
- Add tone selection (professional, friendly, storytelling)
- Hashtag generation
- API response caching
- Docker deployment support

---

## License

This project is intended for learning and portfolio use. Add an open-source license if you plan to distribute it.
