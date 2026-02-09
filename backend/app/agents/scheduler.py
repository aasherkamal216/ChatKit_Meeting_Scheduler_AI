from agents import Agent, StopAtTools
from chatkit.agents import AgentContext
from .tools import search_contacts, find_availability, draft_invite

SCHEDULER_INSTRUCTIONS = """
You are a highly efficient Executive Assistant AI. Your goal is to help the user schedule meetings with precision.

STRICT WORKFLOW RULES:
1. IDENTIFY CONTACTS: If the user wants to book a meeting, first search for the contacts. Use `search_contacts`. Even if the user provides a name, always show the picker to ensure the right person is selected.
2. FIND TIME: Once contacts are confirmed (you will see a user action in tags), call `find_availability`.
3. DRAFT INVITE: After a time slot is picked, use `draft_invite` to show the user the final details. 

IMPORTANT: Never finalize a meeting without showing the `draft_invite` editor first. The user must click the "Send" button in the UI.

TONE: Professional, concise, and helpful.
"""

def build_scheduler_agent() -> Agent[AgentContext]:
    tools = [search_contacts, find_availability, draft_invite]

    return Agent[AgentContext](
        model="gpt-4o-mini",
        name="Executive Scheduler",
        instructions=SCHEDULER_INSTRUCTIONS,
        tools=tools,
        tool_use_behavior=StopAtTools(
            stop_at_tool_names=[
                search_contacts.name,
                find_availability.name,
                draft_invite.name,
            ]
        ),
    )

scheduler_agent = build_scheduler_agent()