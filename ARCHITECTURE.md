# Architecture & Design

Technical deep dive into the bot's modular architecture and design decisions.

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Module Responsibilities](#module-responsibilities)
3. [Data Flow](#data-flow)
4. [Database Schema](#database-schema)
5. [Design Decisions](#design-decisions)
6. [Dependency Graph](#dependency-graph)

---

## Architecture Overview

### Refactoring: Before → After

#### Before: Monolithic
```
bot.py (776 lines)
├── Constants & configuration
├── Database setup & queries
├── Validation functions
├── UI components (Views & Modals)
└── All commands

Problem: Everything mixed together, hard to change one thing without affecting others
```

#### After: Modular
```
bot.py (47 lines) ← Clean entry point
│
├── config/settings.py ← All constants
├── database/db.py ← All database operations
├── utils/validators.py ← All validation
├── views/ ← All button/menu UI
├── modals/ ← All form UI
└── commands/listings.py ← All slash commands

Benefit: Each module has single responsibility, easy to test and modify
```

### Design Principles Used

1. **Separation of Concerns**
   - Database logic → `database/db.py`
   - Validation → `utils/validators.py`
   - UI components → `views/` and `modals/`
   - Commands → `commands/listings.py`

2. **Single Responsibility**
   - Each file does one thing well
   - Easy to find code you need to change
   - Easy to test individual components

3. **Reusability**
   - Validation functions can be imported anywhere
   - Database functions used by multiple commands
   - Views can be used by different commands

4. **Scalability**
   - Easy to add new commands (create new file in `commands/`)
   - Easy to add new validators (add to `utils/validators.py`)
   - Easy to add new database operations (add to `database/db.py`)

---

## Module Responsibilities

### 📁 `config/settings.py` (82 lines)
**Responsibility**: All configuration constants in one place

**Contains**:
```python
# Database
DB_PATH = "auction_house.db"

# Pet database
PETS = {
    "Delve": "https://...",
    "Bramble": "https://...",
    # ... 11 more pets
}

# Validation rules
MAX_QUANTITY = 10000
VALID_RARITIES = ["Legendary", "Mythic"]
MAX_LISTING_SIZE = 50

# Messages
MSG_LISTING_CREATED = "✅ Listing created!"
# ... more messages
```

**Used by**: Every other module

**Example**:
```python
from config.settings import PETS, MAX_QUANTITY, DB_PATH
```

---

### 📁 `database/db.py` (244 lines)
**Responsibility**: All database operations

**Functions**:
- `init_database()` - Create tables on startup
- `get_pet_by_name(pet_name)` - Look up pet info
- `get_all_pets()` - Get all 13 pets
- `create_listing()` - Insert new listing
- `get_user_listings()` - Get all listings for user
- `get_user_listings_filtered()` - Get with filter/sort
- `update_listing()` - Modify existing listing
- `delete_listing()` - Remove listing
- `search_listings()` - Find listings by pet name
- `get_listing_by_id()` - Get specific listing

**Why Separate**:
- All database logic in one place
- Easy to change database (SQLite → PostgreSQL)
- Easy to add new queries
- Easy to test with mock database

**Used by**: Commands, Modals

---

### 📁 `utils/validators.py` (96 lines)
**Responsibility**: Validation and formatting

**Functions**:
- `validate_quantity()` - Check qty is 1-10000
- `validate_rarity()` - Check rarity is Legendary/Mythic
- `parse_quantities()` - Parse "Legendary:5,Mythic:3"
- `format_quantities()` - Format for display
- `format_section()` - Format have/want sections
- `get_quantity_presets()` - Get preset quantities
- `get_filter_options()` - Get filter choices
- `get_sort_options()` - Get sort choices

**Why Separate**:
- Validation logic reusable across commands
- Easy to update validation rules in one place
- Easy to add new validators
- Easy to test validators

**Used by**: Commands, Modals

---

### 📁 `views/listing.py` (86 lines)
**Responsibility**: UI for creating listings

**Classes**:
- `QuantityPresetView` - Buttons for quantity presets
- `ListingTypeView` - Choose HAVE/WANT/BOTH
- `PetListingView` - Add more pets or done

**Why Separate**:
- Focused on listing creation flow
- Easy to modify UI without touching database

**Used by**: Commands

---

### 📁 `views/manage.py` (92 lines)
**Responsibility**: UI for managing listings

**Classes**:
- `MyListingsView` - Actions on listings (edit/delete)
- `EditListingOptionsView` - Choose what to edit
- `EditModeChoiceView` - Replace or add to listing

**Why Separate**:
- Focused on listing management
- Clear separation from creation UI

**Used by**: Commands

---

### 📁 `modals/add_pet.py` (245 lines)
**Responsibility**: Form dialogs for user input

**Classes**:
- `AddPetModal` - Add pet with quantities
- `EditListingSelectModal` - Select listing by ID
- `DeleteListingModal` - Delete listing by ID
- `QuantityPresetButtons` - Preset quantity helper

**Why Separate**:
- Encapsulates form logic
- Easy to modify modal fields
- Keeps UI logic separate from business logic

**Used by**: Views

---

### 📁 `commands/listings.py` (165 lines)
**Responsibility**: All slash commands

**Commands**:
- `/create_listing` - Start listing creation
- `/my_listings` - View user's listings (with filter/sort)
- `/search` - Find listings (with type filter)
- `/help` - Get help
- `/how-to-trade` - Trading guide
- `/pets` - View all pets

**Why Separate**:
- All commands organized in one place
- Easy to add new commands
- Easy to see all available commands

**Used by**: Bot startup

---

### 📁 `bot.py` (47 lines)
**Responsibility**: Application entry point

**Contains**:
```python
# 1. Import all modules
from config.settings import TOKEN
from database.db import init_database
from commands.listings import setup_commands

# 2. Create Discord client
client = discord.Client()
tree = app_commands.CommandTree(client)

# 3. Setup on startup
@client.event
async def on_ready():
    init_database()
    setup_commands(tree, client)
    client._setup_done = True

# 4. Run bot
client.run(TOKEN)
```

**Why So Small**:
- Orchestration only
- All logic is in specialized modules
- Easy to understand at a glance
- Easy to modify startup sequence

---

## Data Flow

### Creating a Listing

```
User Command: /create_listing
    ↓
bot.py calls: create_listing command
    ↓
Command shows: ListingTypeView (choose HAVE/WANT/BOTH)
    ↓
User clicks button
    ↓
Show: QuantityPresetView (helpful tips)
    ↓
Show: AddPetModal (form)
    ↓
User submits form
    ↓
Modal validates: parse_quantities() [utils/validators.py]
    ↓
Modal creates: create_listing() [database/db.py]
    ↓
Show: PetListingView (add more pets or done)
    ↓
User clicks Done
    ↓
Complete ✅
```

### Searching

```
User Command: /search item:Delve
    ↓
Command calls: search_listings("Delve") [database/db.py]
    ↓
Command filters: offers vs requests based on search_type
    ↓
Command formats: Uses format_quantities() [utils/validators.py]
    ↓
Show: Results embed with first 5 + count
```

### Viewing Listings

```
User Command: /my_listings filter_by:have sort_by:most
    ↓
Command calls: get_user_listings_filtered(user_id, "have", "most")
    ↓
Filter Applied: Show only HAVE-only listings
    ↓
Sort Applied: Sort by most items first
    ↓
Format: Using format_quantities() [utils/validators.py]
    ↓
Show: Listings embed with filter/sort info
```

---

## Database Schema

### Listings Table

```sql
CREATE TABLE listings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    haves TEXT,                      -- JSON: {"pet_name": {"Legendary": qty, "Mythic": qty}}
    wants TEXT,                      -- JSON: {"pet_name": {"Legendary": qty, "Mythic": qty}}
    description TEXT,                -- Optional notes
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Example Row

```python
{
    'id': 42,
    'user_id': 123456789,
    'haves': {
        'Delve': {'Legendary': 5, 'Mythic': 0},
        'Bramble': {'Legendary': 3, 'Mythic': 2}
    },
    'wants': {
        'Kragg': {'Legendary': 10, 'Mythic': 0}
    },
    'description': 'Trading Delves and Brambles for Kragg',
    'created_at': '2024-01-15 10:30:00'
}
```

### Pets Table

```sql
CREATE TABLE pets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    image_url TEXT NOT NULL
);
```

### Why This Design

1. **Flexibility**: JSON allows variable number of pet rarities
2. **Simplicity**: Single table for listings
3. **Scalability**: Can extend without schema migration
4. **Performance**: Simple queries for common operations

---

## Design Decisions Explained

### 1. Why Module Per Directory?

**Question**: Why `database/db.py` instead of `database/queries.py`, `database/tables.py`, etc?

**Answer**: 
- ✅ Single module per directory = simpler imports
- ✅ Easy to find database code (all in one file)
- ✅ Follows Python conventions
- ✅ If it gets too large (>300 lines), we split it then

### 2. Why Configuration in Code Instead of Config File?

**Question**: Why not `config.json` for settings?

**Answer**:
- ✅ Constants don't change at runtime
- ✅ Type hints help catch errors
- ✅ No extra file to manage
- ✅ If we need external config later, easy to refactor

### 3. Why `get_user_listings_filtered()` Instead of Multiple Functions?

**Question**: Why not `get_user_listings_have()`, `get_user_listings_by_date()`, etc?

**Answer**:
- ✅ Single function with parameters is more flexible
- ✅ Easier to combine filters and sorts
- ✅ Less function bloat
- ✅ Easier to maintain (one place to update)

### 4. Why Separate `views/listing.py` and `views/manage.py`?

**Question**: Why not combine in one file?

**Answer**:
- ✅ `listing.py` is for creation flow (focused)
- ✅ `manage.py` is for management flow (separate)
- ✅ Each file is understandable (~90 lines)
- ✅ If we add new flows, they get their own files

### 5. Why JSON in Database Instead of Separate Tables?

**Question**: Why not `listing_has_item` and `listing_wants_item` junction tables?

**Answer**:
- ✅ Simpler for small data (max 50 items)
- ✅ All data for listing in one row
- ✅ Faster for our use case
- ✅ If we scale to millions of items, we'd normalize then

---

## Dependency Graph

```
bot.py (orchestration)
├── config/settings.py ← Imported by everyone
├── database/db.py ← Data layer
│   └── uses config/settings.py
├── utils/validators.py ← Utility layer
│   └── uses config/settings.py
├── views/listing.py ← UI layer
│   └── uses modals/add_pet.py
├── views/manage.py ← UI layer
│   └── uses modals/add_pet.py
├── modals/add_pet.py ← Form layer
│   ├── uses database/db.py
│   ├── uses utils/validators.py
│   └── uses config/settings.py
└── commands/listings.py ← Command layer
    ├── uses database/db.py
    ├── uses utils/validators.py
    ├── uses views/listing.py
    ├── uses views/manage.py
    └── uses config/settings.py
```

### Dependency Rules
- ✅ Lower layers don't depend on higher layers
- ✅ `config` is imported by everything
- ✅ `database` and `utils` only import `config`
- ✅ `views` and `modals` import from lower layers
- ✅ `commands` is at the top (imports everything)

This creates a "clean architecture" where you can change lower layers without breaking higher layers.

---

## Scaling This Architecture

### Adding New Commands

1. Create new parameter to existing command
2. Or add new command to `commands/listings.py`
3. Command can use existing database/validator functions

### Adding New Database Operations

1. Add new function to `database/db.py`
2. Import and use in commands/views/modals

### Adding New Validators

1. Add new function to `utils/validators.py`
2. Import and use anywhere validation is needed

### Adding New UI Flows

1. Create new file: `views/new_flow.py` or `modals/new_flow.py`
2. Import in commands
3. Integrate into existing commands

### If `commands/listings.py` Gets Too Large

1. Create new file: `commands/trading.py` for trade-specific commands
2. Import in bot.py and register

### If `database/db.py` Gets Too Large (>300 lines)

1. Split by concern:
   - `database/listings.py` - Listing operations
   - `database/pets.py` - Pet operations
   - `database/queries.py` - Shared queries
2. Import all functions in `database/__init__.py`

---

## Performance Considerations

### Current Optimizations

1. **Database**
   - JSON storage for variable-length data
   - Single table keeps queries simple
   - Indexes on frequently searched columns would help if needed

2. **Validation**
   - Validation happens before database writes
   - Prevents invalid data from being stored

3. **Caching**
   - Pet list cached in `config/settings.py`
   - Gets re-read only at startup

### Future Optimizations If Needed

1. Add database indexes on `user_id` and `created_at`
2. Cache search results temporarily
3. Batch delete operations
4. Pagination for large result sets

---

## Security Considerations

### Current Safeguards

1. **Input Validation**
   - All user quantities validated (1-10000)
   - All pet names validated against database
   - Strings escaped in database queries

2. **Authorization**
   - Each user can only see their own listings
   - Each user can only edit/delete their own listings
   - Verified with `user_id` checks

3. **Error Handling**
   - No sensitive data in error messages
   - Database errors logged but not exposed to user

### Best Practices Followed

- ✅ Never trust user input (all validated)
- ✅ Use parameterized queries (prevent SQL injection)
- ✅ Check authorization before operations
- ✅ Log security-relevant events
- ✅ Don't expose internal errors to users

---

**Architecture Version**: 1.0  
**Status**: Production Ready  
**Last Updated**: Phase 2 Complete
