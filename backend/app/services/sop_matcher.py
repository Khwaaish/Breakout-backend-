"""
SOP (Standard Operating Procedure) Matching Service

Classifies customer messages to appropriate SOP categories
and provides suggested responses.
"""
from typing import Optional, TypedDict


class SOPMatch(TypedDict):
    """Response type for SOP matching"""
    sop: str
    response: str


# ============================================================================
# SOP Definitions
# ============================================================================

PRICING_SOP = {
    "name": "Pricing SOP",
    "keywords": ["price", "pricing", "cost", "charges", "fee", "rate", "quote"],
    "response": "Thank you for reaching out. Our pricing details are available on our website. "
                "For specific quotes, please contact our sales team."
}

BOOKING_SOP = {
    "name": "Booking SOP",
    "keywords": ["book", "appointment", "schedule", "reserve", "booking", "slot", "time"],
    "response": "Please share your preferred date and time. Our team will confirm the appointment shortly."
}

COMPLAINT_SOP = {
    "name": "Complaint SOP",
    "keywords": ["issue", "problem", "complaint", "issue", "broken", "error", "bug", "not working"],
    "response": "We sincerely apologize for the inconvenience. Our support team will contact you shortly to resolve this."
}

AFTER_HOURS_SOP = {
    "name": "After Hours SOP",
    "keywords": ["closed", "tomorrow", "weekend", "after hours", "night", "evening"],
    "response": "Our team will respond during working hours. We appreciate your patience."
}

# SOP registry in priority order
SOPS = [
    PRICING_SOP,
    BOOKING_SOP,
    COMPLAINT_SOP,
    AFTER_HOURS_SOP,
]


def match_sop(message: str) -> Optional[SOPMatch]:
    """
    Match customer message to appropriate SOP category.
    
    Performs case-insensitive keyword matching to classify messages.
    Returns the first matching SOP based on priority order.
    
    Args:
        message: Customer message text
        
    Returns:
        SOPMatch dict with 'sop' and 'response' keys, or None if no match
        
    Example:
        >>> match_sop("Need pricing information")
        {'sop': 'Pricing SOP', 'response': 'Thank you for reaching out...'}
        
        >>> match_sop("Random question")
        None
    """
    if not message or not isinstance(message, str):
        return None
    
    # Normalize message to lowercase for matching
    message_lower = message.lower()
    
    # Check each SOP in priority order
    for sop in SOPS:
        # Check if any keyword matches in the message
        for keyword in sop["keywords"]:
            if keyword.lower() in message_lower:
                return SOPMatch(
                    sop=sop["name"],
                    response=sop["response"]
                )
    
    # No match found
    return None
