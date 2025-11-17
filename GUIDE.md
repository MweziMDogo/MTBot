# Developer Guide & Best Practices

Complete reference for developing and extending the Miner Tycon Bot.

## Table of Contents
1. [Code Style](#code-style)
2. [Common Operations](#common-operations)
3. [Adding Features](#adding-features)
4. [Logging](#logging)
5. [Error Handling](#error-handling)
6. [Type Hints](#type-hints)
7. [Testing](#testing)

---

## Code Style

### Import Organization
```python
# Standard library (alphabetical)
import asyncio
import logging
import sqlite3
from typing import Dict, List, Optional, Tuple, Any

# Third-party libraries (alphabetical)
import discord
from discord import app_commands, ui

# Local imports (alphabetical)
from config.settings import PETS, DB_PATH
from database.db import get_user_listings
from utils.validators import parse_quantities
```

### Naming Conventions
```python
# Constants - UPPER_CASE
MAX_QUANTITY = 10000
VALID_RARITIES = ["Legendary", "Mythic"]

# Functions - snake_case
def validate_quantity(qty: str) -> bool:
    pass

# Classes - PascalCase
class AddPetModal(ui.Modal):
    pass

# Variables - snake_case
user_listings = get_user_listings(user_id)
is_valid = validate_quantity(qty)
```

### Function Documentation
```python
# GOOD - Complete docstring
def get_pet_by_name(pet_name: str) -> Optional[Tuple[str, str, str]]:
    """Get pet info by name (case-insensitive).
    
    Args:
        pet_name: Name of the pet to find
        
    Returns:
        Tuple of (id, name, image_url) or None if not found
        
    Raises:
        sqlite3.Error: If database query fails
        
    Example:
        >>> pet = get_pet_by_name("Delve")
        >>> pet[1]  # Returns "Delve"
    """
    pass

# AVOID - No docstring or incomplete
def get_pet_by_name(pet_name):
    # missing info
    pass
```

### Line Length & Formatting
- **Max line length**: 100 characters
- **Indentation**: 4 spaces
- **Blank lines**: 2 between top-level definitions, 1 between methods

---

## Common Operations

### Working with the Database
```python
from database.db import (
    get_user_listings,
    create_listing,
    update_listing,
    delete_listing,
    search_listings,
    get_pet_by_name
)

# Get user's listings
listings = get_user_listings(user_id=123456)

# Create a listing
listing_id = create_listing(
    user_id=123456,
    haves={"Delve": {"Legendary": 5, "Mythic": 0}},
    wants={"Bramble": {"Legendary": 3, "Mythic": 1}},
    description="Trading Delves for Brambles"
)

# Update a listing
update_listing(
    listing_id=42,
    haves={"Kragg": {"Legendary": 10, "Mythic": 5}}
)

# Delete a listing
delete_listing(listing_id=42)

# Search for listings
results = search_listings(pet_name="Delve")
```

### Validation & Formatting
```python
from utils.validators import (
    validate_quantity,
    validate_rarity,
    parse_quantities,
    format_quantities
)

# Validate a single quantity
is_valid, error_msg = validate_quantity("1000")
if not is_valid:
    print(f"Error: {error_msg}")

# Validate rarity
is_valid, error_msg = validate_rarity("Legendary")

# Parse combined quantity string
is_valid, quantities, error = parse_quantities("Legendary:5,Mythic:3")
# Returns: (True, {"Legendary": 5, "Mythic": 3}, "")

# Format quantities for display
display = format_quantities({"Legendary": 5, "Mythic": 3})
# Returns: "Legendary: 5 | Mythic: 3"
```

### Working with Pets
```python
from database.db import get_all_pets, get_pet_by_name

# Get all pets
all_pets = get_all_pets()  # List of (id, name, image_url)
for pet_id, pet_name, image_url in all_pets:
    print(f"{pet_name}: {image_url}")

# Get specific pet
pet = get_pet_by_name("Delve")
if pet:
    pet_id, pet_name, image_url = pet
```

---

## Adding Features

### Adding a New Command
```python
# In commands/listings.py
from discord import app_commands

@tree.command(name='my_command', description='What it does')
@app_commands.describe(
    param1='Parameter description',
    param2='Another parameter'
)
async def my_command(
    interaction: discord.Interaction,
    param1: str,
    param2: int = 10
):
    """Full command description."""
    try:
        await interaction.response.defer(ephemeral=True)
        
        # Do work here
        result = some_operation(param1, param2)
        
        await interaction.followup.send(
            f"Result: {result}",
            ephemeral=True
        )
    except Exception as e:
        logger.error(f"Error in my_command: {e}", exc_info=True)
        await interaction.followup.send(
            f"❌ Error: {str(e)}",
            ephemeral=True
        )
```

### Adding a New Validator
```python
# In utils/validators.py
def validate_new_thing(value: str) -> Tuple[bool, str]:
    """Validate something.
    
    Args:
        value: The value to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not value:
        return False, "Value cannot be empty"
    
    if len(value) > 100:
        return False, "Value too long (max 100 chars)"
    
    return True, ""
```

### Adding a Database Function
```python
# In database/db.py
def get_something(id: int) -> Optional[Dict[str, Any]]:
    """Get something from database.
    
    Args:
        id: ID to look up
        
    Returns:
        Dictionary with data or None if not found
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM something WHERE id = ?", (id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'name': row[1],
                'data': row[2]
            }
        return None
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}", exc_info=True)
        raise
```

### Adding a View (Buttons)
```python
# In views/listing.py
class MyNewView(ui.View):
    """View with custom buttons."""
    
    def __init__(self, user_id: int):
        super().__init__(timeout=600)
        self.user_id = user_id
    
    @ui.button(label="Click Me", style=discord.ButtonStyle.primary)
    async def button_callback(
        self,
        interaction: discord.Interaction,
        button: ui.Button
    ) -> None:
        """Handle button click."""
        try:
            await interaction.response.send_message(
                "Button clicked!",
                ephemeral=True
            )
        except Exception as e:
            logger.error(f"Error in button: {e}", exc_info=True)
            await interaction.response.send_message(
                f"❌ Error: {str(e)}",
                ephemeral=True
            )
```

### Adding a Modal (Forms)
```python
# In modals/add_pet.py
class MyNewModal(ui.Modal, title="Modal Title"):
    """Modal for user input."""
    
    name_input = ui.TextInput(
        label="Name",
        placeholder="Enter a name...",
        min_length=1,
        max_length=50,
        required=True
    )
    
    description_input = ui.TextInput(
        label="Description",
        placeholder="Optional description...",
        min_length=0,
        max_length=500,
        required=False
    )
    
    async def on_submit(self, interaction: discord.Interaction) -> None:
        """Handle form submission."""
        try:
            name = self.name_input.value.strip()
            description = self.description_input.value.strip()
            
            # Validate
            is_valid, error = validate_something(name)
            if not is_valid:
                await interaction.response.send_message(
                    f"❌ {error}",
                    ephemeral=True
                )
                return
            
            # Process
            await do_something(name, description)
            
            await interaction.response.send_message(
                "✅ Success!",
                ephemeral=True
            )
        except Exception as e:
            logger.error(f"Error in modal: {e}", exc_info=True)
            await interaction.response.send_message(
                f"❌ Error: {str(e)}",
                ephemeral=True
            )
```

---

## Logging

### Logging Best Practices
```python
import logging

logger = logging.getLogger(__name__)

# INFO - Important user actions
logger.info(f"User {user_id} created listing #{listing_id}")
logger.info(f"Search for '{pet_name}' found {len(results)} results")

# WARNING - Unexpected but handled situations
logger.warning(f"Quantity {qty} exceeds limit, capped at {MAX_QTY}")
logger.warning(f"Pet '{name}' not found in database")

# ERROR - Errors that need attention
logger.error(f"Database connection failed: {e}", exc_info=True)
logger.error(f"Failed to parse quantities: {e}", exc_info=True)

# DEBUG - Development only
logger.debug(f"Listing data: {listing_dict}")
logger.debug(f"Processing {len(items)} items")
```

### Logging in Async Functions
```python
async def my_async_function(user_id: int):
    """Do something async."""
    logger.info(f"Starting operation for user {user_id}")
    
    try:
        result = await some_operation()
        logger.info(f"Operation completed: {result}")
        return result
    except Exception as e:
        logger.error(
            f"Operation failed for user {user_id}: {e}",
            exc_info=True  # Include stack trace
        )
        raise
```

---

## Error Handling

### Try/Except Pattern
```python
async def my_command(interaction: discord.Interaction):
    """Handle errors gracefully."""
    try:
        await interaction.response.defer(ephemeral=True)
        
        # Do work
        result = do_something()
        
        await interaction.followup.send(f"✅ {result}")
    except ValueError as e:
        # User input error - show friendly message
        logger.warning(f"Invalid input: {e}")
        await interaction.followup.send(f"❌ {str(e)}")
    except sqlite3.Error as e:
        # Database error - log and show generic message
        logger.error(f"Database error: {e}", exc_info=True)
        await interaction.followup.send(
            "❌ Database error. Try again later."
        )
    except Exception as e:
        # Unexpected error - log details
        logger.error(f"Unexpected error: {e}", exc_info=True)
        await interaction.followup.send(
            "❌ An unexpected error occurred."
        )
```

### Custom Error Messages
```python
# GOOD - Clear, actionable messages
"❌ Pet 'Delve' not found. Use /pets to see available pets."
"❌ Quantity must be 1-10000, got 50000"
"❌ Listing #42 not found or doesn't belong to you"

# AVOID - Vague messages
"❌ Error"
"❌ Invalid input"
"❌ Something went wrong"
```

---

## Type Hints

### Type Hint Guidelines
```python
from typing import Dict, List, Optional, Tuple, Any, Union

# Function arguments
def process_listing(
    user_id: int,
    haves: Dict[str, Dict[str, int]],
    wants: Optional[Dict[str, Dict[str, int]]] = None,
    description: str = ""
) -> int:  # Returns listing ID
    """Process a listing."""
    pass

# Variables
listings: List[Dict[str, Any]] = []
user_count: int = 0
is_valid: bool = True
result: Optional[str] = None

# Union types for multiple possibilities
def process_item(item: Union[str, int]) -> bool:
    """Handle string or int."""
    pass

# Tuples
def get_pet() -> Tuple[int, str, str]:  # (id, name, url)
    pass
```

### Type Hints for Async Functions
```python
from typing import Optional
import discord

async def my_async_function(user_id: int) -> Optional[str]:
    """Return string or None."""
    return "result"

# In callbacks
async def button_callback(
    self,
    interaction: discord.Interaction,
    button: ui.Button
) -> None:
    """Buttons don't return values."""
    pass
```

---

## Testing

### Manual Testing Checklist
```
For each new command:
- [ ] Command shows in autocomplete
- [ ] Command description is clear
- [ ] Parameters work with defaults
- [ ] Error cases handled gracefully
- [ ] Error messages are helpful
- [ ] Logs show operation details

For database functions:
- [ ] Can create new records
- [ ] Can read existing records
- [ ] Can update records
- [ ] Can delete records
- [ ] Edge cases handled (empty, not found, etc.)

For validators:
- [ ] Valid inputs pass
- [ ] Invalid inputs fail
- [ ] Error messages are clear
- [ ] Edge cases handled
```

### Example Test Cases
```python
# Testing a validator
def test_validate_quantity():
    # Valid cases
    assert validate_quantity("1000")[0] == True
    assert validate_quantity("1")[0] == True
    
    # Invalid cases
    assert validate_quantity("0")[0] == False  # Too low
    assert validate_quantity("50000")[0] == False  # Too high
    assert validate_quantity("abc")[0] == False  # Not a number
```

---

## Quick Checklist for New Features

- [ ] Function has docstring with Args, Returns, Raises
- [ ] Type hints on all parameters and return values
- [ ] Logging for important operations (info level)
- [ ] Logging for errors (error level with exc_info=True)
- [ ] Error handling with try/except
- [ ] User-friendly error messages
- [ ] Code follows style guidelines
- [ ] No magic numbers (use constants from config)
- [ ] Tested manually before committing
- [ ] Related documentation updated

---

**Last Updated**: Phase 2 Complete  
**Version**: 1.0
