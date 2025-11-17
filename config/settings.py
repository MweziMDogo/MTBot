"""Bot configuration and constants."""

import os

# Database
DB_PATH = 'database/auction_house.db'

# Pet Management
PETS = [
    ('Delve', 'https://cdn.discordapp.com/emojis/1439426782406246524.webp?size=96'),
    ('Bramble', 'https://cdn.discordapp.com/emojis/1439427181095944454.webp?size=96'),
    ('Kragg', 'https://cdn.discordapp.com/emojis/1439427215631843398.webp?size=96'),
    ('Malgrim', 'https://cdn.discordapp.com/emojis/1429474495889936494.webp?size=96'),
    ('Mimic', 'https://cdn.discordapp.com/emojis/1439427321219125400.webp?size=96'),
    ('Smolder', 'https://cdn.discordapp.com/emojis/1429474259759140904.webp?size=96'),
    ('Vyra', 'https://cdn.discordapp.com/emojis/1439427265040486561.webp?size=96'),
    ('Luma', 'https://cdn.discordapp.com/emojis/1429473389705167079.webp?size=96'),
    ('Oblivion', 'https://cdn.discordapp.com/emojis/1429474805593145425.webp?size=96'),
    ('Weave', 'https://cdn.discordapp.com/emojis/1438188450506473532.webp?size=96'),
    ('Embi', 'https://cdn.discordapp.com/emojis/1436084498034065580.webp?size=96'),
    ('Aurelia', 'https://cdn.discordapp.com/emojis/1439409968725098606.webp?size=96'),
    ('Grimm', 'https://cdn.discordapp.com/emojis/1438188479132467341.webp?size=96'),
]

VALID_RARITIES = ('Legendary', 'Mythic')
MAX_QUANTITY = 10000

# Pagination
ITEMS_PER_PAGE = 5  # Results per page in search

# Timeouts
MODAL_TIMEOUT = 300  # 5 minutes for modal responses
VIEW_TIMEOUT_SHORT = 600  # 10 minutes for temporary views
VIEW_TIMEOUT_PERSISTENT = None  # Persistent views (no timeout)

# Feature Flags
ENABLE_SEARCH_PAGINATION = True
ENABLE_BULK_OPERATIONS = False  # Future: bulk edit/delete
ENABLE_TRADING = False  # Future: direct trading system

# Messages
MSG_LISTING_CREATED = "✅ Created listing for {pet_text}!\n\n**Add another pet or click Done**"
MSG_LISTING_UPDATED = "✅ {action} {section} section: {section_text}\n\n**Updated {section}:** {full_section}\n**Listing #{listing_id} has been updated!**"
MSG_LISTING_DELETED = "✅ Listing #{listing_id} has been deleted."
MSG_NO_LISTINGS = "You don't have any listings yet. Use `/create_listing` to create one!"
MSG_INVALID_PET = "❌ Pet '{pet_name}' not found in database.\nAvailable pets: {available_pets}"
MSG_INVALID_QUANTITY = "❌ Invalid quantities. Must be numbers between 0 and {max_qty}"
MSG_NO_SEARCH_RESULTS = "No matching listings found."
