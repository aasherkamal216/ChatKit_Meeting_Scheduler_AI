import os
from typing import List, Dict, Any
from chatkit.widgets import WidgetTemplate, WidgetRoot
from app.types import Contact

# Helper to get template path
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")

def get_template_path(filename: str) -> str:
    return os.path.join(TEMPLATE_DIR, filename)

# Load Templates
contact_picker_tmpl = WidgetTemplate.from_file(get_template_path("contact_picker.widget"))
time_picker_tmpl = WidgetTemplate.from_file(get_template_path("time_picker.widget"))
invite_editor_tmpl = WidgetTemplate.from_file(get_template_path("invite_editor.widget"))
meeting_confirmed_tmpl = WidgetTemplate.from_file(get_template_path("meeting_confirmed.widget"))

def build_contact_picker(contacts: List[Contact]) -> WidgetRoot:
    """
    Hydrates the Contact Picker with a list of Contact objects.
    """
    payload = {
        "contacts": [
            {
                "id": c.id,
                "name": c.name,
                "role": c.role,
                "avatar_url": c.avatar_url or "https://i.pravatar.cc/162?u=" + c.id
            } for c in contacts
        ]
    }
    return contact_picker_tmpl.build(payload)

def build_time_picker(slots: List[Dict[str, Any]]) -> WidgetRoot:
    """
    Hydrates the Time Picker.
    Expected slot dict: {"id": str, "time_label": str, "duration": str, "conflict": bool}
    """
    return time_picker_tmpl.build({"slots": slots})

def build_invite_editor(
    subject: str, 
    agenda: str, 
    location: str, 
    attendees: str, 
    time_str: str
) -> WidgetRoot:
    """
    Hydrates the HITL Invite Editor.
    """
    payload = {
        "subject": subject,
        "agenda": agenda,
        "location": location,
        "attendees": attendees,
        "time_str": time_str
    }
    return invite_editor_tmpl.build(payload)

def build_meeting_confirmed(subject: str, time_str: str) -> WidgetRoot:
    """
    Hydrates the static final confirmation card.
    """
    return meeting_confirmed_tmpl.build({
        "subject": subject,
        "time_str": time_str
    })