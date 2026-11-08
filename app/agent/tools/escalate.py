from app.agent.tools.base import Tool, ToolResult


class EscalateToHumanTool(Tool):
    """Tool to escalate requests to human staff with structured categories."""
    
    ACTION_ENUMS = {
        "category": ["complaint", "special_request", "booking_issue", "billing", "accessibility", "group_booking", "corporate", "media", "other"],
        "contact_preference": ["phone", "email", "in_person"],
    }
    
    ESCALATION_CATEGORIES = {
        "complaint": "Guest complaint about stay, service, or facilities",
        "special_request": "Complex request requiring human coordination",
        "booking_issue": "Problem with existing reservation",
        "billing": "Question about charges, invoice, or payment",
        "accessibility": "Accessibility needs requiring staff coordination",
        "group_booking": "Large group or event booking inquiry",
        "corporate": "Corporate account or business travel inquiry",
        "media": "Press or media inquiry",
        "other": "Other reason requiring human attention",
    }
    
    @property
    def name(self) -> str:
        return "escalate_to_human"
    
    @property
    def description(self) -> str:
        return "Escalate the user's request to hotel staff. Use when the user asks to speak to a human, has a complaint, or has a complex request. Provide a category and reason."
    
    async def execute(
        self,
        reason: str,
        user_message: str,
        category: str = "other",
        guest_name: str | None = None,
        booking_id: str | None = None,
        contact_preference: str | None = None,  # "phone", "email", "in_person"
    ) -> ToolResult:
        try:
            # Validate category
            if category not in self.ESCALATION_CATEGORIES:
                category = "other"
            
            # In production, this would integrate with a ticketing system, email, or messaging platform
            escalation_id = f"ESC-{hash(user_message + reason + category) % 100000:05d}"
            
            return ToolResult(success=True, data={
                "escalation_id": escalation_id,
                "category": category,
                "category_description": self.ESCALATION_CATEGORIES[category],
                "message": "Your request has been forwarded to our hotel staff. They will contact you shortly.",
                "guest_name": guest_name,
                "booking_id": booking_id,
                "contact_preference": contact_preference,
                "note": "No actual human contact has been made - this is a simulation until real integration exists.",
            })
        except Exception as e:
            return ToolResult(success=False, error=str(e))