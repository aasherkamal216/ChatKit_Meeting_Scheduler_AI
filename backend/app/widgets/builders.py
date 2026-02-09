import os
from typing import List, Dict, Any
from pydantic import TypeAdapter  # Added this
from chatkit.widgets import WidgetTemplate, WidgetRoot
from app.types import Contact

# Helper to get template path
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")

# Pydantic TypeAdapter to handle validation for the WidgetRoot Union type
widget_root_adapter = TypeAdapter(WidgetRoot)


def get_template_path(filename: str) -> str:
    return os.path.join(TEMPLATE_DIR, filename)


# Load Templates
contact_picker_tmpl = WidgetTemplate.from_file(
    get_template_path("contact_picker.widget")
)
time_picker_tmpl = WidgetTemplate.from_file(get_template_path("time_picker.widget"))
invite_editor_tmpl = WidgetTemplate.from_file(get_template_path("invite_editor.widget"))
meeting_confirmed_tmpl = WidgetTemplate.from_file(
    get_template_path("meeting_confirmed.widget")
)


def build_contact_picker(contacts: List[Contact]) -> WidgetRoot:
    payload = {
        "contacts": [
            {
                "id": c.id,
                "name": c.name,
                "role": c.role,
                "avatar_url": c.avatar_url or "https://i.pravatar.cc/162?u=" + c.id,
            }
            for c in contacts
        ]
    }
    return contact_picker_tmpl.build(payload)


def build_time_picker(slots: List[Dict[str, Any]]) -> WidgetRoot:
    return time_picker_tmpl.build({"slots": slots})


def build_invite_editor(
    subject: str, 
    agenda: str, 
    location: str, 
    attendees: str, 
    time_str: str
) -> WidgetRoot:
    payload = {
        "subject": subject,
        "agenda": agenda,
        "location": location,
        "attendees": attendees,
        "time_str": time_str,
    }
    return invite_editor_tmpl.build(payload)


def build_meeting_confirmed(subject: str, time_str: str) -> WidgetRoot:
    return meeting_confirmed_tmpl.build({"subject": subject, "time_str": time_str})


def build_selection_locked(title: str, detail: str) -> WidgetRoot:
    """
    Builds a read-only card to replace an interactive widget after selection.
    """
    payload = {
        "type": "Card",
        "size": "sm",
        "children": [
            {
                "type": "Row",
                "align": "center",
                "gap": 3,
                "children": [
                    {
                        "type": "Box",
                        "background": "green-500",
                        "radius": "full",
                        "size": 24,
                        "align": "center",
                        "justify": "center",
                        "children": [
                            {
                                "type": "Icon",
                                "name": "check",
                                "color": "white",
                                "size": "sm",
                            }
                        ],
                    },
                    {
                        "type": "Col",
                        "gap": 0,
                        "children": [
                            {"type": "Caption", "value": title, "color": "secondary"},
                            {"type": "Text", "value": detail, "weight": "semibold"},
                        ],
                    },
                ],
            }
        ],
    }
    # Use the adapter instead of calling model_validate on the Type Alias
    return widget_root_adapter.validate_python(payload)
