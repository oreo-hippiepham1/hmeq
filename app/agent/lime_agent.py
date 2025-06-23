from ast import List
from pydantic_ai import Agent, capture_run_messages
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.exceptions import UnexpectedModelBehavior
from pydantic import BaseModel, Field, model_validator, ValidationError

from langgraph.graph import StateGraph, START, END

from app.agent.prompts import LIME_PROMPT

from dotenv import load_dotenv
import os
from typing import TypedDict, Tuple, List
import asyncio

load_dotenv()


# 0.5 --- Define Prompt (other module)
# 1 --- Define structured output (not fully necessary here)
class LimeAgentOutput(BaseModel):
    lime_interpretation: str = Field(description="The response to the user's question")
    financial_advice: str = Field(description="The financial advice to the user")


# 2 --- Initialize the agent
lime_agent = Agent(
    model=OpenAIModel(model_name="gpt-4.1-mini"),
    output_type=LimeAgentOutput,
    system_prompt=LIME_PROMPT,
)


# 3 --- Managed with LangGraph
class LimeGraphMessage(TypedDict):
    default_probability: float
    lime_explanations: List[Tuple[str, float]]
    agent_response_lime: str
    agent_response_advice: str


# 4 --- Define the graph
async def agent_node(message: LimeGraphMessage) -> dict:
    full_query = f"""
    Loan default probability: {message["default_probability"]}
    Lime explanations: {message["lime_explanations"]}
    """
    with capture_run_messages() as messages:
        try:
            response = await lime_agent.run(full_query)
            agent_output: LimeAgentOutput = response.output

            return {
                "agent_response_lime": agent_output.lime_interpretation,
                "agent_response_advice": agent_output.financial_advice,
            }
        except UnexpectedModelBehavior as e:
            print(f"Error during agent run: {e}")
            print(f"Cause: {e.__cause__}")
            print(f"Messages: {messages}")
            raise e


# 5 --- Define the graph
def create_graph():
    """
    Create the state graph for the agent.
    """
    print("Creating graph")
    graph = StateGraph(LimeGraphMessage)

    # Add nodes to the graph
    graph.add_node("lime_agent", agent_node)

    # Edges
    graph.add_edge(START, "lime_agent")
    graph.add_edge("lime_agent", END)

    app = graph.compile()
    print("Graph created")
    return app


async def test_run():
    app = create_graph()
    result = await app.ainvoke(
        LimeGraphMessage(
            default_probability=0.8,
            lime_explanations=[
                ("JOB is not Office", 0.5),
                ("CLAGE <= 109.41", 0.3),
                ("DEBTINC > 35.5", 0.2),
            ],
        )
    )
    print(result["agent_response_lime"])
    print(result["agent_response_advice"])
    return result


# 6 --- Run the graph
if __name__ == "__main__":
    asyncio.run(test_run())
