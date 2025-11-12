# StoryAI

A Flask backend and Streamlit frontend-based web app for creating, managing, and roleplaying via characters with an LLM Agent. It supports user accounts, character creation with a point-buy system, image uploads for character portraits, and generating narrative/decisions with an LLM.

## Table of Contents
- Overview
- Features
- Architecture
- Quick Start
- Configuration
- Usage
- File-by-file overview
- Further Advancements
- Acknowledgement

## Overview
This project provides:
- User and character management with a point-buy attribute system, backstory etc.
- Image uploads for character portraits
- Chat histories per character
- Skill checks via dice rolling
- AI-powered narrative with decision helpers using LangChain and an LLM Provider (e.g., OpenAI).
- Built with a Flask backend and a Streamlit frontend.

## Features
- User and character management (create, list, delete)
- Point-buy character attributes with configurable limits
- Uploads folder for portraits
- Chat history persistence
- LLM-backed agents for character description/decisions to influence the narrative
- Streamlit chat interface that connects to the Flask backend

## Architecture
- Backend: Flask app (application factory plus a simple app module), SQLAlchemy models and managers, chat/character/user components.
- Frontend: Streamlit single-page app for chatting and browsing character conversation histories.
- Storage: SQL database (SQLite by default; configurable), uploads directory for images.
- Templates: Jinja2
- AI: LangChain + LLM provider

## Repository structure
- application.py — Flask application factory (create_app) and project root handling, including database initialization (SQLAlchemy)
- streamlit_chat.py — Streamlit UI, reads BACKEND_URL and URL params and runs the chat interaction
- backend_app.py — Simple Flask app instance used for running the application and configuration constants (e.g., BASE_TOTAL, MAX_POINTS, UPLOAD_FOLDER)
- users.py — User model (ORM)
- characters.py — Character model (ORM)
- chat_history.py — ChatHistory model (ORM)
- user_manager.py — UserManager service (uses db, User, Character)
- character_manager.py — CharacterManager service (uses db, User, Character)
- chat_manager.py — ChatManager service (uses db, ChatHistory)
- dice_roll.py — Skill check rolling utility
- chat_routes.py — Chat-related route registrations (backend)
- chat_with_agent.py — Backend glue for interacting with agents 
- narrative_agent.py — Narrative/content generation agent 
- decision_agent.py — Decision-making agent with system prompt 
- filter_agent.py — Filtering/backstory agent and LLM configuration

## Quick Start

### Prerequisites
- Python 3.10+ recommended
- pip and virtualenv (or your preferred environment manager)

### Setup
1. Clone and create a virtual environment
2. Install dependencies via PowerShell
   a. pip install -r requirements.txt
3. Create an environment file (.env) in the dir where backend_app.py is with
   a. SECRET_KEY for session security in Flask
   b. OPENAI_API_KEY for the use of the agents
   c. LANGSMITH_API_KEY for the use of the agents
4. To start the backend and streamlit chat each in their own PowerShell:
   a. python backend_app.py (if using win)
   b. streamlit run streamlit_chat.py

## Configurations

- SECRET_KEY: Required for session security in Flask.
- DATABASE_URL: SQLite URL in application.py
- UPLOAD_FOLDER: Directory for images and similar assets in backend_app.py
- BASE_TOTAL, MAX_POINTS: Controls character attribute distribution in backend_app.py
- BACKEND_URL: Used by the Streamlit app to contact the Flask backend set in streamlit_chat.py
- LLM_API_KEY, LLM_MODEL: Set if you will use the agents.

Use environment variables in the specified .py files or your .env file to configure these values.

## Usage
- Visit the home page to create a user.
- Add characters to a user and distribute attribute points using the point-buy system.
- Upload a character image for a portrait.
- If you’ve configured an LLM API key, you can generate or refine backstories, personalities, and other flavor details.
- Run skill checks and track character-specific chat history as needed.

## Further Advancements:

- using Javascript/React o. something similar to enhance the webpages
- full separation between front- and backend with this
- make the dice roll interactive in streamlit
- extend the prompt to give the user a chance to select a storyline
- extend the prompt to enhance the storyline with premade characters
- give the user a meaning to update/change their char
- add proficiencies

## Acknowledgement

Placeholder Image:
Image: "Portrait Placeholder.png" by Greasemann, licensed under CC BY-SA 4.0 / Source: [Link to the Wikimedia Commons file page](https://commons.wikimedia.org/wiki/File:Portrait_Placeholder.png)

### License
This project is licensed under the MIT License-see the LICENSE file for details.