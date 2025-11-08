import getpass
import os
from typing import List, Optional

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

# Define here which chatbot to use TODO let user choose
CHATBOT_MODEL = 'gpt-4o-mini'

load_dotenv()

# load LangSmith API Key and GPT API Key
if not os.environ.get('OPENAI_API_KEY'):
    openai_key = os.getenv('OPENAI_API_KEY')
    if openai_key:
        os.environ['OPENAI_API_KEY'] = openai_key
    else:
        os.environ['OPENAI_API_KEY'] = getpass.getpass("Enter API key for OpenAI: ")

if not os.environ.get('LANGSMITH_API_KEY'):
    os.environ['LANGSMITH_API_KEY'] = "true"
    os.environ['LANGSMITH_API_KEY'] = os.getenv('LANGSMITH_API_KEY')

#Initialize language model
llm = ChatOpenAI(model=CHATBOT_MODEL, temperature=0)

# Filter for Backstory, Personality, Appearance, Proficiency
class RelevantElements(BaseModel):
    """
    Schema to filter if there is relevant Backstory
    """
    rel_story_elem : Optional[List[str]] = Field(default=None, description=
                                        "A list of relevant elements given the context and user action."
                                        "Return an empty List if none are relevant.")

# Agent

def create_filter_agent(agent_type, schema):
    """
    Creates filter agent for each category.
    """
    SYSTEM_PROMPT = f"""
    You are a filter agent. Your only job is to analyze the users action from the user_message
    and the current story context and select only the most relevant items from the provided character data.
    
    Your task is to select relevant {agent_type} elements only from the data provided in the character data and context.
    
    Rules:
    1. You must output a JSON object strictly adhering to the provided schema.
    2. Be extremely strict in your assessment. If an item id not directly relevant to the action or current scene,
    do not include it.
    """

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            ("user", "Character data: {character_data}\n\n "
                     "Context: {context}\n\n "
                     "User's latest action:{user_action}"),
        ]
    )

    return(
        RunnablePassthrough()
        | prompt
        | llm.with_structured_output(schema=schema)
    )

# Instantiate Agents
backstory_agent = create_filter_agent("backstory", RelevantElements)
personality_agent = create_filter_agent("personality", RelevantElements)
appearance_agent = create_filter_agent("appearance", RelevantElements)
proficiency_agent = create_filter_agent("proficiencies", RelevantElements)