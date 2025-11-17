"""Database operations and initialization."""

import sqlite3
import json
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from config.settings import DB_PATH, PETS

logger = logging.getLogger(__name__)


def init_database() -> None:
    """Initialize the auction house database with tables if they don't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create pets table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            image_url TEXT NOT NULL
        )
    ''')

    # Create listings table with timestamps
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS listings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            haves TEXT NOT NULL DEFAULT '{}',
            wants TEXT NOT NULL DEFAULT '{}',
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create trades table for price tracking
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            gave_pet TEXT NOT NULL,
            gave_qty INTEGER NOT NULL,
            gave_rarity TEXT NOT NULL,
            received_pet TEXT NOT NULL,
            received_qty INTEGER NOT NULL,
            received_rarity TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Add missing columns if they don't exist (migration)
    cursor.execute("PRAGMA table_info(listings)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'created_at' not in columns:
        cursor.execute('ALTER TABLE listings ADD COLUMN created_at TIMESTAMP')
        logger.info('Added created_at column to listings table')
    
    if 'updated_at' not in columns:
        cursor.execute('ALTER TABLE listings ADD COLUMN updated_at TIMESTAMP')
        logger.info('Added updated_at column to listings table')

    conn.commit()

    # Populate pets table if empty
    cursor.execute('SELECT COUNT(*) FROM pets')
    if cursor.fetchone()[0] == 0:
        cursor.executemany(
            'INSERT INTO pets (name, image_url) VALUES (?, ?)',
            PETS
        )
        conn.commit()
        logger.info(f'Loaded {len(PETS)} pets into database')

    conn.close()


def get_pet_by_name(pet_name: str) -> Optional[tuple]:
    """
    Retrieve a pet by name from the database.

    Args:
        pet_name: The name of the pet to retrieve

    Returns:
        Tuple of (id, name, image_url) or None if not found
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, image_url FROM pets WHERE LOWER(name) = LOWER(?)', (pet_name,))
    result = cursor.fetchone()
    conn.close()
    return result


def get_all_pets() -> List[tuple]:
    """
    Retrieve all pets from the database.

    Returns:
        List of tuples (id, name, image_url)
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, image_url FROM pets ORDER BY name')
    results = cursor.fetchall()
    conn.close()
    return results


def create_listing(user_id: int, haves: Dict[str, int], wants: Dict[str, int], description: str = '') -> int:
    """
    Create a new listing for a user.

    Args:
        user_id: Discord user ID
        haves: Dictionary of pet names to quantities they have
        wants: Dictionary of pet names to quantities they want
        description: Optional description

    Returns:
        ID of the created listing
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    haves_json = json.dumps(haves)
    wants_json = json.dumps(wants)

    cursor.execute(
        '''INSERT INTO listings (user_id, haves, wants, description)
           VALUES (?, ?, ?, ?)''',
        (user_id, haves_json, wants_json, description)
    )

    conn.commit()
    listing_id = cursor.lastrowid
    conn.close()

    logger.info(f'Created listing {listing_id} for user {user_id}')
    return listing_id


def get_user_listings(user_id: int) -> List[Dict[str, Any]]:
    """
    Retrieve all listings for a user.

    Args:
        user_id: Discord user ID

    Returns:
        List of listing dictionaries
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        '''SELECT id, haves, wants, description, created_at, updated_at
           FROM listings WHERE user_id = ? ORDER BY created_at DESC''',
        (user_id,)
    )
    rows = cursor.fetchall()
    conn.close()

    listings = []
    for row in rows:
        listings.append({
            'id': row[0],
            'haves': json.loads(row[1]),
            'wants': json.loads(row[2]),
            'description': row[3],
            'created_at': row[4],
            'updated_at': row[5],
        })

    return listings


def get_listing_by_id(listing_id: int) -> Optional[Dict[str, Any]]:
    """
    Retrieve a specific listing by ID.

    Args:
        listing_id: ID of the listing

    Returns:
        Listing dictionary or None if not found
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        '''SELECT id, user_id, haves, wants, description, created_at, updated_at
           FROM listings WHERE id = ?''',
        (listing_id,)
    )
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return {
        'id': row[0],
        'user_id': row[1],
        'haves': json.loads(row[2]),
        'wants': json.loads(row[3]),
        'description': row[4],
        'created_at': row[5],
        'updated_at': row[6],
    }


def update_listing(listing_id: int, haves: Dict[str, int] = None, wants: Dict[str, int] = None, description: str = None) -> bool:
    """
    Update a listing.

    Args:
        listing_id: ID of the listing
        haves: Updated haves dictionary (optional)
        wants: Updated wants dictionary (optional)
        description: Updated description (optional)

    Returns:
        True if successful, False otherwise
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get current listing
    current = get_listing_by_id(listing_id)
    if not current:
        return False

    # Use current values if not provided
    new_haves = json.dumps(haves if haves is not None else current['haves'])
    new_wants = json.dumps(wants if wants is not None else current['wants'])
    new_description = description if description is not None else current['description']

    cursor.execute(
        '''UPDATE listings 
           SET haves = ?, wants = ?, description = ?, updated_at = CURRENT_TIMESTAMP
           WHERE id = ?''',
        (new_haves, new_wants, new_description, listing_id)
    )

    conn.commit()
    conn.close()

    logger.info(f'Updated listing {listing_id}')
    return True


def delete_listing(listing_id: int) -> bool:
    """
    Delete a listing.

    Args:
        listing_id: ID of the listing

    Returns:
        True if successful, False otherwise
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM listings WHERE id = ?', (listing_id,))
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()

    if success:
        logger.info(f'Deleted listing {listing_id}')

    return success


def search_listings(pet_name: Optional[str] = None, search_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Search listings by pet name and/or listing type.

    Args:
        pet_name: Pet name to search for (searches both haves and wants)
        search_type: 'HAVE', 'WANT', or None for all

    Returns:
        List of matching listings
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT id, user_id, haves, wants, description, created_at, updated_at FROM listings')
    rows = cursor.fetchall()
    conn.close()

    results = []
    for row in rows:
        listing = {
            'id': row[0],
            'user_id': row[1],
            'haves': json.loads(row[2]),
            'wants': json.loads(row[3]),
            'description': row[4],
            'created_at': row[5],
            'updated_at': row[6],
        }

        # Filter by pet name and type
        if pet_name:
            pet_lower = pet_name.lower()
            has_pet = False

            if search_type in [None, 'HAVE']:
                if any(p.lower() == pet_lower for p in listing['haves'].keys()):
                    has_pet = True

            if search_type in [None, 'WANT'] and not has_pet:
                if any(p.lower() == pet_lower for p in listing['wants'].keys()):
                    has_pet = True

            if not has_pet:
                continue

        results.append(listing)

    return results


def get_user_listings_filtered(user_id: int, filter_type: str = 'all', sort_by: str = 'newest') -> List[Dict[str, Any]]:
    """
    Retrieve user listings with filtering and sorting.

    Args:
        user_id: Discord user ID
        filter_type: 'all', 'have', 'want', or 'both'
        sort_by: 'newest', 'oldest', 'most', or 'least'

    Returns:
        Filtered and sorted list of listings
    """
    listings = get_user_listings(user_id)

    # Apply filter
    if filter_type == 'have':
        listings = [l for l in listings if l['haves'] and not l['wants']]
    elif filter_type == 'want':
        listings = [l for l in listings if l['wants'] and not l['haves']]
    elif filter_type == 'both':
        listings = [l for l in listings if l['haves'] and l['wants']]

    # Apply sorting
    if sort_by == 'oldest':
        listings.sort(key=lambda x: x['created_at'] or '', reverse=False)
    elif sort_by == 'most':
        listings.sort(key=lambda x: len(x['haves']) + len(x['wants']), reverse=True)
    elif sort_by == 'least':
        listings.sort(key=lambda x: len(x['haves']) + len(x['wants']))
    else:  # newest (default)
        listings.sort(key=lambda x: x['created_at'] or '', reverse=True)

    return listings


def record_trade(user_id: int, gave_pet: str, gave_qty: int, gave_rarity: str, 
                received_pet: str, received_qty: int, received_rarity: str) -> int:
    """
    Record a completed trade for price tracking.
    
    Args:
        user_id: Discord user ID
        gave_pet: Pet name they gave
        gave_qty: Quantity given
        gave_rarity: Rarity of pet given
        received_pet: Pet name they received
        received_qty: Quantity received
        received_rarity: Rarity of pet received
    
    Returns:
        ID of the recorded trade
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO trades (user_id, gave_pet, gave_qty, gave_rarity, received_pet, received_qty, received_rarity)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, gave_pet, gave_qty, gave_rarity, received_pet, received_qty, received_rarity))
    
    trade_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return trade_id


def get_average_prices(pet_name: str, days: int = 30) -> Dict[str, Any]:
    """
    Get average trade prices for a pet over the last N days.
    
    Args:
        pet_name: Name of the pet
        days: Number of days to look back (default 30)
    
    Returns:
        Dictionary with average prices for each rarity
    """
    from datetime import datetime, timedelta
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cutoff_date = datetime.now() - timedelta(days=days)
    
    # Get trades where this pet was given (incoming trades)
    cursor.execute('''
        SELECT gave_rarity, received_pet, received_qty, received_rarity
        FROM trades
        WHERE LOWER(gave_pet) = LOWER(?)
        AND created_at > ?
        ORDER BY created_at DESC
    ''', (pet_name, cutoff_date.isoformat()))
    
    trades = cursor.fetchall()
    conn.close()
    
    # Group by rarity of the pet being given
    prices_by_rarity = {}
    
    for gave_rarity, received_pet, received_qty, received_rarity in trades:
        key = f"{gave_rarity}"
        
        if key not in prices_by_rarity:
            prices_by_rarity[key] = {
                'rarity': gave_rarity,
                'trades': []
            }
        
        prices_by_rarity[key]['trades'].append({
            'received_pet': received_pet,
            'received_qty': received_qty,
            'received_rarity': received_rarity
        })
    
    # Calculate averages
    result = {
        'pet_name': pet_name,
        'days': days,
        'total_trades': len(trades),
        'by_rarity': {}
    }
    
    for rarity, data in prices_by_rarity.items():
        result['by_rarity'][rarity] = {
            'rarity': data['rarity'],
            'trade_count': len(data['trades']),
            'avg_price': _calculate_avg_price(data['trades'])
        }
    
    return result


def _calculate_avg_price(trades: List[Dict[str, Any]]) -> str:
    """
    Calculate average price from trades as a formatted string.
    
    Args:
        trades: List of trade dictionaries
    
    Returns:
        Formatted average price string
    """
    if not trades:
        return "No data"
    
    # Group by received pet/rarity and count occurrences
    price_summary = {}
    
    for trade in trades:
        key = f"{trade['received_pet']} ({trade['received_rarity']})"
        if key not in price_summary:
            price_summary[key] = 0
        price_summary[key] += trade['received_qty']
    
    # Create readable string
    items = [f"{qty}x {pet}" for pet, qty in sorted(price_summary.items())]
    return " + ".join(items) if items else "No trades"
