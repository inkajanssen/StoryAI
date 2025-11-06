import getpass
import os
from typing import Literal, Optional

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

DecisionType = Literal["skill_check", "narrative_continues"]

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


class CoreDecisions(BaseModel):
    """
    Schema to decide whether a dice roll has to be made or the narrative agent should be triggered.
    """
    next_action: DecisionType = (Field(..., description="The next action the LLM decides to make: "
                                                        "'skill_check' if a roll is needed "
                                                        "or 'narrative_continues' for dialogue or description."))
    ability: Optional[str] = Field(default=None, description="Required D&D Ability if there is a 'skill_check' "
                                          "(e.g. 'Strength, 'Dexterity,...'). "
                                          "Otherwise must be none if next_action is 'narrative_continues'.")
    ability_score: Optional[int] = Field(default=None,
                                         description= "The corresponding ability score number to the ability used "
                                                      "if there is a 'skill_check'. "
                                                      "0 if its 'narrative_continues'.")
    dc: Optional[int] = Field(default=None, description= "Required if next_action is a 'skill_check.'"
                                                         "The target difficulty for the roll, "
                                                         "the higher the more difficult the activity gets."
                                                         "0 if the next_action is 'narrative_continues'.")

    response_text: str = Field(..., description="If the decisiontype is 'skill check' its a short description "
                                                "that leads into the roll. "
                                                "If its 'narrative_continues' respond with the context to give to the narrative agent.")

SYSTEM_PROMPT = """
You are the Core Decision Agent for a D&D 5e-style text adventure.
Your only job is to analyze the user' latest message and the chats current context and output a structured JSON object 
that determines the NEXT step in the story. 

Rules:
1. Output must strictly adhere to the provided JSON Schema CoreDecisions.
2. If the user attempts an action that requires a chance of failure/success and is narratively necessary,
set DecisionType to 'skill_check' and provide the required roll parameters like ability, ability_score, dc and response text.
3. Incorporate the characters personality and backstory into the decision if a skill check is necessary or if the character
can automatically succeed.
4. If you set the DecisionType to 'skill_check' the parameters should be filled as to their description.
The ability fits the action made.
The score comes from the context provided.
The dc is determined by how difficult the action is normally. 
The response text should be a brief narrative description of the check made.
5. If the user does not want to make an action that requires a role, set DecisionType to 'narrative_continues', set the parameter
ability, ability_score and dc to null.
"""

#Initialize language model
llm = ChatOpenAI(model=CHATBOT_MODEL, temperature=0)

# Create prompt_template
prompt_template = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        ("user", "Context: {context}\n\nUser's latest action: {user_action}"),
    ]
)

# Bind the structured output to the LLM
# Chain creation
core_decisions = (
    RunnablePassthrough.assign(context=lambda x:x.get("context", "No context provided"))
    | prompt_template
    | llm.with_structured_output(schema=CoreDecisions)
)

# Callable Agent
async def run_core_decisions(context, user_action):
    """
    Analyses user action in context and returns a JSON Schema.
    """
    try:
        result = await core_decisions.ainvoke({
            "context": context,
            "user_action": user_action
        })

        if isinstance(result, CoreDecisions):
            return result
        else:
            raise ValueError("LLM did not return the expected structured object.")
    except Exception as e:
        print(f"Error invoking agent: {e}")
        return CoreDecisions(
            next_action='narrative_continues',
            response_text=f"The AI encountered an error:{e}.Please reload.",
        )