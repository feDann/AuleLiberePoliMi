# Aule Libere PoliMi Bot

[![Start Bot](https://img.shields.io/badge/Telegram-Start_Bot-blue?style=for-the-badge&logo=telegram)](https://t.me/polimiAuleLibereBot)
![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker)
![License](https://img.shields.io/badge/License-GPLv3-green?style=for-the-badge)

A powerful Telegram bot designed to help **Politecnico di Milano** students find free classrooms for studying.
Since the official PoliMi website no longer allows easy searching for free spaces, this bot fills the gap by scraping real-time data and filtering it based on your needs.

---

## Get Started

Ready to find a classroom? Start chatting with the bot now!

[**🤖 Start AuleBot**](https://t.me/polimiAuleLibereBot)

---

## Features

- **Smart Search**: Find free classrooms by Campus, Day, and Time slot.
- **Power Plugs 🔌**: Instantly see which classrooms have power outlets available.
- **Customizable Interface**: Toggle between **Emoji Mode** (compact) and **Classic Text Mode** via settings.
- **High Performance**: Implements **Intelligent Caching** (1 hour TTL) to ensure instant responses for repeated queries.
- **Granular Opening Hours**: Automatically respects specific building schedules
- **Multi-language**: Fully localized in **Italian** 🇮🇹 and **English** 🇬🇧.
- **Docker Ready**: Zero-config deployment with Docker and Docker Compose.
- **User Friendly**: Interactive keyboards and "Quick Search" (Now) button.

---

## Deployment

### Option A: Docker (Recommended)

The easiest way to run the bot is using Docker. You don't need to install Python or dependencies manually.

#### 1. Run with Docker CLI
```bash
docker run -d \
  --name aulebot \
  -e TOKEN="YOUR_TELEGRAM_BOT_TOKEN" \
  --restart unless-stopped \
  ghcr.io/gorlix/auleliberepolimi:latest
```

#### 2. Run with Docker Compose
The repository already includes a `docker-compose.yml` file.
Simply edit `docker-compose.yml` to set your `TOKEN` (or use an `.env` file), and run:

```bash
docker-compose up -d
```

---

### Option B: Manual Installation

If you prefer running it directly on your machine:

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/gorlix/AuleLiberePoliMi.git
    cd AuleLiberePoliMi
    ```

2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure Environment**:
    Create a `.env` file in the root directory:
    ```env
    TOKEN=your_telegram_bot_token
    ```

4.  **Run the Bot**:
    ```bash
    python3 bot.py
    ```

---

## Credits

- **Maintainer**: [Alessandro Gorla (Gorlix)](https://github.com/gorlix)
- **Original Author**: [FeDann](https://github.com/feDann)

---

## License
This project is licensed under the GPL-3.0 License - see the LICENSE file for details.
