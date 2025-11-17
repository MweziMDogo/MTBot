"""Utility functions for validation and data processing."""

import logging
from typing import Dict, Tuple, Optional
from config.settings import MAX_QUANTITY, VALID_RARITIES

logger = logging.getLogger(__name__)


def validate_quantity(quantity: str) -> Tuple[bool, str]:
    """
    Validate quantity input.

    Args:
        quantity: Quantity as string

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        qty = int(quantity)
        if qty < 1 or qty > MAX_QUANTITY:
            return False, f"❌ Quantity must be between 1 and {MAX_QUANTITY}"
        return True, ""
    except ValueError:
        return False, f"❌ '{quantity}' is not a valid number"


def validate_rarity(rarity: str) -> Tuple[bool, str]:
    """
    Validate rarity input.

    Args:
        rarity: Rarity value

    Returns:
        Tuple of (is_valid, error_message)
    """
    if rarity not in VALID_RARITIES:
        return False, f"❌ '{rarity}' is not a valid rarity. Valid options: {', '.join(VALID_RARITIES)}"
    return True, ""


def parse_quantities(input_str: str) -> Tuple[bool, Dict[str, int], str]:
    """
    Parse quantity input in format "rarity:quantity".

    Args:
        input_str: String like "Legendary:5" or "Mythic:10"

    Returns:
        Tuple of (is_valid, parsed_dict, error_message)
    """
    quantities = {}

    # Split by comma and process each entry
    entries = [e.strip() for e in input_str.split(',') if e.strip()]

    for entry in entries:
        # Format: "Rarity:Quantity"
        if ':' not in entry:
            return False, {}, f"❌ Invalid format: '{entry}'. Use 'Rarity:Quantity' (e.g., 'Legendary:5')"

        parts = entry.split(':')
        if len(parts) != 2:
            return False, {}, f"❌ Invalid format: '{entry}'. Use 'Rarity:Quantity'"

        rarity = parts[0].strip()
        qty_str = parts[1].strip()

        # Validate rarity
        is_valid, error_msg = validate_rarity(rarity)
        if not is_valid:
            return False, {}, error_msg

        # Validate quantity
        is_valid, error_msg = validate_quantity(qty_str)
        if not is_valid:
            return False, {}, error_msg

        quantities[rarity] = int(qty_str)

    if not quantities:
        return False, {}, "❌ No valid quantities provided"

    return True, quantities, ""


def format_quantities(quantities: Dict[str, int]) -> str:
    """
    Format quantities dictionary for display.

    Args:
        quantities: Dictionary of rarity to quantity

    Returns:
        Formatted string for display
    """
    if not quantities:
        return "None"

    parts = []
    for rarity in VALID_RARITIES:
        if rarity in quantities:
            parts.append(f"**{rarity}:** {quantities[rarity]}")

    return " | ".join(parts) if parts else "None"


def format_section(section_dict: Dict[str, int], pet_name: str) -> str:
    """
    Format a section (HAVE/WANT) for display.

    Args:
        section_dict: Dictionary of {pet_name: {rarity: quantity}}
        pet_name: Name of pet to format

    Returns:
        Formatted string
    """
    if not section_dict or pet_name not in section_dict:
        return "None"

    quantities = section_dict[pet_name]
    return format_quantities(quantities)


def get_quantity_presets() -> Dict[str, int]:
    """
    Get common quantity presets for quick selection.

    Returns:
        Dictionary of preset names to quantities
    """
    return {
        "1": 1,
        "10": 10,
        "50": 50,
        "100": 100,
        "1000": 1000,
    }


def get_modal_instructions() -> str:
    """
    Get formatted instructions for the modal.

    Returns:
        Formatted instruction string
    """
    return (
        "Format: **Rarity:Quantity**\n"
        "Examples: `Legendary:5` or `Mythic:10`\n"
        "Max quantity: 10,000 per rarity\n"
        "Leave blank for 0"
    )


def get_sort_options() -> Dict[str, str]:
    """
    Get available sorting options for listings.

    Returns:
        Dictionary of sort key to description
    """
    return {
        "newest": "Newest first",
        "oldest": "Oldest first",
        "most": "Most items first",
        "least": "Least items first",
    }


def get_filter_options() -> Dict[str, str]:
    """
    Get available filter options for listings.

    Returns:
        Dictionary of filter key to description
    """
    return {
        "all": "All listings",
        "have": "HAVE only",
        "want": "WANT only",
        "both": "BOTH only",
    }
