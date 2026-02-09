from datetime import datetime
from typing import List, Dict
from agents import RunContextWrapper, function_tool
from chatkit.agents import AgentContext
from chatkit.types import (
    ThreadItemDoneEvent,
    AssistantMessageItem,
    AssistantMessageContent,
)
from app.store.app_store import search_contacts_in_db
from app.widgets.builders import (
    build_contact_picker,
    build_time_picker,
    build_invite_editor,
)


async def _send_assistant_message(ctx: RunContextWrapper[AgentContext], text: str):
    """Helper to stream a text message from within a tool."""
    await ctx.context.stream(
        ThreadItemDoneEvent(
            item=AssistantMessageItem(
                thread_id=ctx.context.thread.id,
                id=ctx.context.generate_id("message"),
                created_at=datetime.now(),
                content=[AssistantMessageContent(text=text)],
            ),
        )
    )


@function_tool()
async def search_contacts(
    ctx: RunContextWrapper[AgentContext], query: str
) -> Dict[str, str]:
    """
    Searches the user's address book for contacts matching a name or email. This tool displays a visual Contact Picker widget to the user.
    Parameter: query (e.g., 'Bob' or 'bob@example.com')
    """
    user_id = ctx.context.request_context.user_id
    contacts = await search_contacts_in_db(user_id, query)

    if not contacts:
        msg = f"I'm sorry, I couldn't find any contacts matching '{query}'."
        await _send_assistant_message(ctx, msg)
        return {"status": "error", "message": "No contacts found."}

    # 1. Stream the text explanation
    await _send_assistant_message(
        ctx,
        f"I found {len(contacts)} contacts. Please select the ones you'd like to invite.",
    )

    # 2. Stream the widget
    widget = build_contact_picker(contacts)
    await ctx.context.stream_widget(widget)

    # 3. Return summary to Agent memory
    return f"SUCCESS: Displayed Contact Picker widget with the following matches: {contacts}. Waiting for user to confirm selection via UI action."


@function_tool(
    description_override="Check availability and find open time slots for a group of attendees. It displays a time picker widget with the best options."
)
async def find_availability(
    ctx: RunContextWrapper[AgentContext], attendee_ids: List[str]
) -> Dict[str, str]:
    # Mocked slots
    slots = [
        {
            "id": "slot_1",
            "time_label": "Today, 2:00 PM",
            "duration": "1 hour",
            "conflict": False,
        },
        {
            "id": "slot_2",
            "time_label": "Today, 4:30 PM",
            "duration": "30 mins",
            "conflict": True,
        },
        {
            "id": "slot_3",
            "time_label": "Tomorrow, 10:00 AM",
            "duration": "1 hour",
            "conflict": False,
        },
    ]

    await _send_assistant_message(
        ctx,
        "I've analyzed the schedules for all participants. Here are the best available slots:",
    )

    widget = build_time_picker(slots)
    await ctx.context.stream_widget(widget)

    return f"Analyzed availability for attendees {attendee_ids} and displayed time picker widget to user."


@function_tool()
async def draft_invite(
    ctx: RunContextWrapper[AgentContext],
    subject: str,
    agenda: str,
    slot_time_str: str,
    attendee_names: str,
    location: str = "Zoom",
) -> Dict[str, str]:
    """Create a draft meeting invitation widget and display it to the user for review. Use this BEFORE sending any invite.

    Args:
        subject (str): The subject of the meeting.
        agenda (str): The agenda of the meeting.
        slot_time_str (str): The time slot for the meeting.
        attendee_names (str): A comma-separated list of attendee names.
        location (str, optional): The location of the meeting. Defaults to "Zoom".
    """
    await _send_assistant_message(
        ctx,
        "I've drafted the invitation. Please review the agenda and subject below. You can edit them directly if needed.",
    )

    widget = build_invite_editor(
        subject=subject,
        agenda=agenda,
        location=location,
        attendees=attendee_names,
        time_str=slot_time_str,
    )
    await ctx.context.stream_widget(widget)

    return f"Drafted meeting invite with subject '{subject}' for attendees {attendee_names} and displayed invite editor widget to user."


@function_tool()
async def check_schedule(ctx: RunContextWrapper[AgentContext]) -> str:
    """
    Retrieves the user's current schedule and list of booked meetings.
    """
    user_id = ctx.context.request_context.user_id
    from app.store.app_store import (
        get_events_by_user,
    )  # local import to avoid circularity

    events = await get_events_by_user(user_id)

    if not events:
        return "Your calendar is currently empty. No meetings are scheduled."

    summary = "Here are your scheduled meetings:\n"
    for e in events:
        summary += f"- {e['subject']} at {e['start_time']} with {e['attendees']} (Location: {e['location']})\n"

    return summary