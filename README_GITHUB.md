# Miner Tycon Bot

A Discord bot for trading and managing virtual pet collections with a clean, modular architecture.

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- Discord Bot Token from [Discord Developer Portal](https://discord.com/developers/applications)

### Installation (Windows)

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/miner-tycon-bot.git
   cd miner-tycon-bot
   ```

2. **Run setup** (installs all dependencies)
   ```bash
   setup.bat
   ```

3. **Configure bot token**
   - Create a `.env` file in the project directory
   - Add your Discord bot token:
     ```
     DISCORD_BOT_TOKEN=your_token_here
     ```

4. **Start the bot**
   ```bash
   start_bot.bat
   ```

### Installation (Linux/Mac)

```bash
# Clone repository
git clone https://github.com/yourusername/miner-tycon-bot.git
cd miner-tycon-bot

# Install dependencies
pip install -r requirements.txt

# Create .env file
echo "DISCORD_BOT_TOKEN=your_token_here" > .env

# Run bot
python bot.py
```

---

## 📋 Commands

### User Commands
- `/create_listing` - Create a new HAVE/WANT listing for trading
- `/search <pet>` - Find listings by pet name
- `/my_listings` - View and manage your listings (filter, sort, edit, delete)
- `/help` - View comprehensive help documentation
- `/how-to-trade` - Learn step-by-step trading process
- `/pets` - Display all available 13 pets

### Price Tracking
- `/record_trade <pet> <rarity> <qty>` - Record a completed trade
- `/price_chart <pet>` - View average price history for a pet
- `/market_overview` - See most-traded pets and average prices

### Admin Commands
- `/admin_listings` - View all listings in database
- `/admin_delete_listing <id>` - Delete a specific listing
- `/admin_clear_user_listings <user_id>` - Remove all listings from a user
- `/admin_edit_listing <id>` - Edit listing content
- `/admin_add <user_id>` - Add a new admin (no restart needed)
- `/admin_remove <user_id>` - Remove admin user
- `/admin_list` - View all current admins

---

## 🏗️ Project Structure

```
miner-tycon-bot/
├── bot.py                          # Entry point
├── requirements.txt                # Dependencies
├── .env                           # Discord token (create this)
├── setup.bat                      # One-click setup (Windows)
├── start_bot.bat                  # One-click start (Windows)
├── .gitignore                     # Git ignore rules
├── README.md                      # This file
├── SETUP.md                       # Detailed setup guide
├── GUIDE.md                       # User guide
├── CHANGELOG.md                   # Version history
├── ARCHITECTURE.md                # Technical architecture
│
├── commands/
│   ├── listings.py               # 8 listing commands
│   ├── pricing.py                # 3 price tracking commands
│   ├── admin.py                  # 7 admin management commands
│   └── __init__.py
│
├── database/
│   ├── db.py                     # Database operations
│   ├── auction_house.db          # SQLite database
│   └── __init__.py
│
├── config/
│   ├── settings.py               # Bot configuration & constants
│   └── __init__.py
│
├── modals/
│   ├── add_pet.py                # Listing creation modal
│   ├── trade_modal.py            # Trade recording modal
│   └── __init__.py
│
├── views/
│   ├── listing.py                # Listing UI components
│   ├── manage.py                 # Listing management UI
│   └── __init__.py
│
├── utils/
│   ├── validators.py             # Input validation
│   └── __init__.py
│
├── scripts/
│   └── populate_sample_data.py    # Sample data generator
│
└── logs/
    └── bot.log                   # Runtime logs
```

---

## 🗄️ Database

The bot uses SQLite3 with the following tables:

### `listings` (Trading Offers)
- `id` - Unique listing ID
- `user_id` - Discord user ID
- `haves` - JSON: items user has
- `wants` - JSON: items user wants
- `description` - Optional notes
- `created_at` - Timestamp
- `updated_at` - Timestamp

### `pets` (Pet Catalog)
13 available pets: Delve, Bramble, Kragg, Malgrim, Mimic, Smolder, Goblin, Wyvern, Wraith, Succubus, Dragon, Leviathan, Shade

### `trades` (Price History)
- Records of completed trades for price tracking
- Used for `/price_chart` and `/market_overview`

---

## 🔐 Security

- Admin controls require authentication
- All admin actions are logged
- Confirmation required for destructive actions
- Sensitive data (bot token) in `.env` (git-ignored)

---

## 🛠️ Configuration

Edit `config/settings.py` to:
- Add/remove pets
- Change rarity tiers
- Modify database location
- Adjust bot behavior

---

## 📝 Features

✅ **Modular Architecture** - Clean separation of concerns
✅ **18 Commands** - Comprehensive feature set
✅ **Admin Management** - Dynamic admin system without restarts
✅ **Price Tracking** - Market analysis with trade history
✅ **Data Validation** - Input sanitization and type checking
✅ **Error Handling** - Graceful error management with logging
✅ **SQLite Database** - Lightweight, portable data storage
✅ **Discord UI** - Modals, buttons, embeds for great UX

---

## 🚀 Deployment

### GitHub Hosting
1. Push to GitHub repository
2. Use hosting services like:
   - [Heroku](https://www.heroku.com/) (free tier ended)
   - [Render](https://render.com/)
   - [Railway](https://railway.app/)
   - [Replit](https://replit.com/)

### Self-Hosted (Recommended for Production)
- Run on a VPS or dedicated server
- Use systemd (Linux) to manage bot process
- Set up automatic backups for database

---

## 📄 License

MIT License - Feel free to modify and distribute

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first.

---

## 📧 Support

For issues or questions, open a GitHub issue with:
- Description of the problem
- Steps to reproduce
- Bot logs (if applicable)
- Python version and OS

---

## 🎯 Roadmap

- [ ] Persistent admin list (database storage)
- [ ] Web dashboard for price analytics
- [ ] Inventory management system
- [ ] Trading notifications
- [ ] Custom pet rarities per server
- [ ] Auction house leaderboards

---

**Made with ❤️ for the Miner Tycon community**
