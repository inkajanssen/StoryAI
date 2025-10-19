import os
import getpass
from dotenv import load_dotenv
from typing import Sequence, Annotated, TypedDict

from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, trim_messages
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, StateGraph
from langgraph.graph.message import add_messages

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

# Initiate AI model
model = ChatOpenAI(model=CHATBOT_MODEL, temperature=0.7)

# Define State
class State(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    language: str

#Create system prompt
system_prompt = (
            "You are a dungeon master."
            "Your task is to create a story for the user and use their answer to further the story."
            "Keep your responses engaging and challenge the user with choices."
            "Your first message is the beginning of a story in 500 characters or less."
)


# Create prompt template
prompt_template = ChatPromptTemplate.from_messages(
    [
        ("system",system_prompt),
        MessagesPlaceholder(variable_name="messages"),
    ]
)

# Define a trimmer for history managment
trimmer = trim_messages(
    max_tokens=65,
    strategy="last",
    token_counter=model,
    include_system=True,
    allow_partial=False,
    start_on="human",
)

# Define the graph
def create_chatbot():
    workflow = StateGraph(state_schema=State)

    def call_model(state:State):
        #Trim messages
        trimmed_messages = trimmer.invoke(state["messages"])
        prompt = prompt_template.invoke({
            "messages": trimmed_messages,
            "language": state["language"]
        })
        response = model.invoke(prompt)
        return {"messages": [response]}

    workflow.add_edge(START, "model")
    workflow.add_node("model", call_model)
    workflow.add_edge("model", "model")

    memory = MemorySaver()
    return workflow.compile(checkpointer=memory)