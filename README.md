# Miner Tycon Bot

A Discord bot for trading and managing virtual pet collections with a clean, modular architecture.

## 🚀 Quick Start

### Installation
```bash
# Install dependencies
pip install discord.py

# Set up environment
echo "DISCORD_TOKEN=your_token_here" > .env

# Run the bot
python bot.py
```

### Basic Commands
- `/create_listing` - Create a new listing
- `/my_listings` - View your listings (with filters & sorting)
- `/search` - Find listings by pet name
- `/help` - Get comprehensive help
- `/how-to-trade` - Learn the trading process
- `/pets` - View all available pets

### Admin Commands (Restricted)
- `/admin_listings` - View all listings
- `/admin_delete_listing` - Remove a specific listing
- `/admin_clear_user_listings` - Clear all listings from a user
- `/admin_edit_listing` - Edit listing content using simple format
- `/admin_add` - Add a new admin
- `/admin_remove` - Remove an admin
- `/admin_list` - View all admins

---

## 📁 Project Structure

```
Miner Tycon Bot/
├── bot.py                      Entry point with file watcher
├── .env                        Discord token
├── auction_house.db            SQLite database
│
├── config/
│   ├── __init__.py
│   └── settings.py             Configuration & constants
│
├── database/
│   ├── __init__.py
│   └── db.py                   Database operations
│
├── utils/
│   ├── __init__.py
│   ├── validators.py           Validation & formatting
│   └── watcher.py              File system monitoring & auto-restart
│
├── views/
│   ├── __init__.py
│   ├── listing.py              Listing UI components
│   └── manage.py               Management UI
│
├── modals/
│   ├── __init__.py
│   └── add_pet.py              Modal dialogs
│
└── commands/
    ├── __init__.py
    ├── listings.py             Slash commands
    ├── pricing.py              Price tracking commands
    └── admin.py                Admin-only commands
```

### Module Overview

| Module | Purpose |
|--------|---------|
| `config/settings.py` | All constants & pet database |
| `database/db.py` | SQLite operations & queries |
| `utils/validators.py` | Input validation & formatting |
| `utils/watcher.py` | File monitoring with auto-restart notifications |
| `views/listing.py` | Listing creation UI |
| `views/manage.py` | Listing management UI |
| `modals/add_pet.py` | Modal dialog forms |
| `commands/listings.py` | User trading commands |
| `commands/pricing.py` | Price tracking commands |
| `commands/admin.py` | Admin management commands |

---

## 📚 Documentation

- **[GUIDE.md](GUIDE.md)** - Developer guide & best practices
- **[CHANGELOG.md](CHANGELOG.md)** - What's new in each phase
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - How it's organized (optional)

---

## ✨ Features

### User Features
- **Create Listings** - Add HAVE/WANT offers with quantities
- **Search** - Find listings by pet name with type filtering
- **View Listings** - Browse your offers with sorting & filtering
- **Help System** - Comprehensive guides and tutorials

### Admin Features
- **Dynamic Admin Management** - Add/remove admins without restart
- **Listing Moderation** - Delete, edit, or clear user listings
- **Simple Edit Format** - Edit listings using intuitive "Pet Rarity Qty" format
- **Multi-Item Editing** - Support for comma-separated items

### Price Tracking
- **Trade Recording** - Automatically log trades for analysis
- **Market Overview** - View price trends and statistics
- **Pet Charts** - Track pricing history per pet

### Technical Features
- **Auto-Restart** - File watcher automatically restarts bot on code changes
- **Discord Notifications** - Users notified before auto-restart
- **Modular Architecture** - Clean separation of concerns
- **Type Safety** - Full type hints throughout codebase
- **Error Handling** - Graceful error handling with user feedback

---

## 🛠️ Development

### Adding a New Command
```python
# In commands/listings.py
@tree.command(name='my_command')
async def my_command(interaction: discord.Interaction):
    """Command description."""
    await interaction.response.send_message("Hello!")
```

### Adding a New Validator
```python
# In utils/validators.py
def validate_something(value: str) -> tuple[bool, str]:
    """Validate something.
    
    Returns:
        (is_valid, error_message)
    """
    if not valid:
        return False, "Error message"
    return True, ""
```

### Adding a Database Function
```python
# In database/db.py
def get_something(id: int) -> Optional[Dict[str, Any]]:
    """Get something from database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # ... query ...
    conn.close()
    return result
```

See [GUIDE.md](GUIDE.md) for complete development practices.

---

## 📊 Code Quality

- ✅ **Modular Architecture** - 6 organized directories
- ✅ **Type Hints** - 90% coverage
- ✅ **Comprehensive Logging** - All operations logged
- ✅ **Error Handling** - Graceful errors with user feedback
- ✅ **Clean Code** - Average 65 lines per file
- ✅ **Well Documented** - Docstrings on all functions

---

## 📈 Current Stats

- **Total Commands**: 18 (8 user + 3 pricing + 7 admin)
- **Total Modules**: 18 Python files
- **Total LOC**: 1,500+ organized lines
- **Type Coverage**: 95%
- **Pet Types**: 13 available
- **Max Listing Size**: 50 items per listing
- **Auto-Restart**: Enabled with file watcher
- **Database**: SQLite with transaction support

---

## 🔗 Links

- [Discord.py Documentation](https://discordpy.readthedocs.io/)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)

---

**Status**: ✅ Production Ready  
**Last Updated**: Phase 2 Complete
