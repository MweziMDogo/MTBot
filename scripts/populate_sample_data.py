"""Script to populate database with sample trades and listings for testing."""

import sqlite3
import sys
import os
from datetime import datetime, timedelta
import random

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import DB_PATH

def add_sample_trades():
    """Add sample trades to the database for price tracking."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Sample trade data
    sample_trades = [
        # Aurelia trades
        (123456789, "Aurelia", 10, "Legendary", "Bramble", 5, "Legendary"),
        (123456789, "Aurelia", 8, "Legendary", "Delve", 6, "Legendary"),
        (987654321, "Aurelia", 5, "Legendary", "Kragg", 3, "Legendary"),
        (111111111, "Aurelia", 12, "Legendary", "Oblivion", 8, "Legendary"),
        (222222222, "Aurelia", 7, "Mythic", "Aurelia", 15, "Legendary"),
        
        # Bramble trades
        (123456789, "Bramble", 4, "Legendary", "Delve", 3, "Legendary"),
        (987654321, "Bramble", 6, "Legendary", "Aurelia", 10, "Legendary"),
        (111111111, "Bramble", 9, "Legendary", "Kragg", 5, "Legendary"),
        
        # Oblivion trades
        (123456789, "Oblivion", 2, "Mythic", "Aurelia", 5, "Legendary"),
        (222222222, "Oblivion", 3, "Mythic", "Bramble", 8, "Legendary"),
        (987654321, "Oblivion", 1, "Mythic", "Delve", 2, "Legendary"),
    ]
    
    # Insert trades with dates spread over the last 30 days
    for i, (user_id, gave_pet, gave_qty, gave_rarity, rec_pet, rec_qty, rec_rarity) in enumerate(sample_trades):
        # Spread trades over 30 days
        days_ago = random.randint(0, 29)
        trade_date = datetime.now() - timedelta(days=days_ago)
        
        cursor.execute('''
            INSERT INTO trades (user_id, gave_pet, gave_qty, gave_rarity, received_pet, received_qty, received_rarity, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, gave_pet, gave_qty, gave_rarity, rec_pet, rec_qty, rec_rarity, trade_date.isoformat()))
    
    conn.commit()
    conn.close()
    print(f"✅ Added {len(sample_trades)} sample trades to database!")


def add_sample_listings():
    """Add sample listings to the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    sample_listings = [
        (111111111, '{"Aurelia": {"Legendary": 50, "Mythic": 3}}', '{"Bramble": {"Legendary": 10}}', "Selling Aurelia, looking for Bramble"),
        (222222222, '{"Oblivion": {"Mythic": 5}}', '{"Aurelia": {"Legendary": 20}, "Delve": {"Legendary": 15}}', "Have Oblivion Mythic, need Aurelia and Delve"),
        (333333333, '{"Delve": {"Legendary": 30}}', '{}', "Selling Delve Legendary only"),
        (444444444, '{}', '{"Kragg": {"Legendary": 5}, "Oblivion": {"Mythic": 1}}', "Looking for Kragg and Oblivion Mythic"),
        (555555555, '{"Bramble": {"Legendary": 15, "Mythic": 2}}', '{"Aurelia": {"Legendary": 25}}', "Trading Bramble for Aurelia"),
    ]
    
    for user_id, haves, wants, desc in sample_listings:
        cursor.execute('''
            INSERT INTO listings (user_id, haves, wants, description)
            VALUES (?, ?, ?, ?)
        ''', (user_id, haves, wants, desc))
    
    conn.commit()
    conn.close()
    print(f"✅ Added {len(sample_listings)} sample listings to database!")


if __name__ == "__main__":
    print("📊 Populating database with sample data...")
    add_sample_trades()
    add_sample_listings()
    print("✅ Done! Bot now has sample data for testing price charts and listings.")
