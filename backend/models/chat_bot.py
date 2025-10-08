import os
import getpass
from dotenv import load_dotenv
from typing import Sequence
from typing_extensions import Annotated, TypedDict

from langchain.chains.summarize.map_reduce_prompt import prompt_template
from langchain.chat_models import init_chat_model
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage, trim_messages
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
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
model = init_chat_model(CHATBOT_MODEL, model_provider='openai')

# Define State
class State(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    language: str

# Create prompt template
prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a dungeon master."
            "Your task is to create a story for the user and use their answer to further the story."
            "Your first message is the beginning of a story in 500 characters or less.",
        ),
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

    memory = MemorySaver()
    return workflow.compile(checkpointer=memory)

chatbot_app = create_chatbot()