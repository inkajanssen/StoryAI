# import getpass
# import os
# from dotenv import load_dotenv
# from langchain.agents import initialize_agent, AgentType, load_tools, agent
# from langchain_openai import OpenAI
# from pydantic import BaseModel
#
# # Define here which chatbot to use TODO let user choose
# CHATBOT_MODEL = 'gpt-4o-mini'
#
# load_dotenv()
#
# # load LangSmith API Key and GPT API Key
# if not os.environ.get('OPENAI_API_KEY'):
#     openai_key = os.getenv('OPENAI_API_KEY')
#     if openai_key:
#         os.environ['OPENAI_API_KEY'] = openai_key
#     else:
#         os.environ['OPENAI_API_KEY'] = getpass.getpass("Enter API key for OpenAI: ")
#
# if not os.environ.get('LANGSMITH_API_KEY'):
#     os.environ['LANGSMITH_API_KEY'] = "true"
#
#
# #Initialize language model
# llm = OpenAI(model=CHATBOT_MODEL, temperature=0)
#
# # Load tools
# tools = load_tools(#put tools here, llm=llm)
#
# # Initialize the agent
# agent = initialize_agent(
#         tools,
#         llm,
#         agent = AgentType.ZERO_SHOT_REACT_DESCRIPTION,
#         verbose = True
# )
#
# # Test agent
#
# prompt = "This should be a prompt"
# response = agent.run(prompt)
# print(response)