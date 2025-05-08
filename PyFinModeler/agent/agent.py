import nest_asyncio
import json
import os
import re
from openai import AsyncOpenAI
from typing import List, Dict, Any, TypedDict
from pydantic import BaseModel, Field, ValidationError
import asyncio

nest_asyncio.apply()

open_ai_api_key = os.environ.get("OPENAI_API_KEY")
client = AsyncOpenAI(api_key=open_ai_api_key)

class AnalystAgentContext(TypedDict):
    company: Dict[str, Any]
    transcripts: List[str]
    target_item: str

class AnalystAgentOutput(BaseModel):
    target_financial: str
    analysis: str
    next_4_qs: Dict[str, float]
    reasoning: str
    conviction_score: int = Field(ge=0, le=10)
    
def analyst_instructions(context: AnalystAgentContext) -> str:
    return f"""
        Analyze this '{context['target_item']}' for the company '{context['company']['name']}', based on historical financial data, market context, industry dynamics, and management commentary extracted from provided earnings call transcripts.
        """.strip()

async def run_analyst_agent(context: AnalystAgentContext, assistant_id: str) -> AnalystAgentOutput:
    
    # Combine instructions and data clearly in one message
    instructions = analyst_instructions(context)
    data_summary = json.dumps(context, indent=2)

    full_message = (
        f"{instructions}\n\n"
        "Here is the necessary data for your analysis:\n"
        f"{data_summary}"
    )

    thread = await client.beta.threads.create()

    await client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=full_message
    )

    run = await client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_id
    )

    while True:
        run_status = await client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        if run_status.status in ["completed", "failed", "expired"]:
            break
        await asyncio.sleep(1)

    if run_status.status != "completed":
        raise RuntimeError(f"Assistant run failed or expired: {run_status.status}")

    messages = await client.beta.threads.messages.list(thread_id=thread.id)
    content = messages.data[0].content[0].text.value.strip()

    # print("Assistant raw output:\n", content)  # Debugging output

    json_match = re.search(r'```(?:json)?\n(.*?)```', content, re.DOTALL)
    if not json_match:
        json_match = re.search(r'{.*}', content, re.DOTALL)

    if json_match:
        json_content = json_match.group(1) if len(json_match.groups()) >= 1 else json_match.group(0)
    else:
        raise ValueError("Could not find valid JSON in the assistant's response")

    try:
        parsed_output = json.loads(json_content.strip())
        validated_output = AnalystAgentOutput(**parsed_output)
        return validated_output.model_dump()

    except (json.JSONDecodeError, ValidationError) as e:
        print("Validation or parsing error:", e)
        print("Extracted JSON was:", json_content)
        raise e
