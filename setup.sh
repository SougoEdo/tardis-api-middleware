#!/bin/bash

echo "=========================================="
echo "  Tardis Download Service Setup"
echo "=========================================="
echo ""

# Check if .env exists
if [ -f .env ]; then
    echo "⚠️  .env file already exists!"
    read -p "Do you want to overwrite it? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Setup cancelled."
        exit 1
    fi
fi

# Copy example env file
cp .env.example .env
echo "✅ Created .env file from template"
echo ""

# Prompt for required variables
echo "📋 Please provide the following required information:"
echo ""

read -p "Tardis API Key: " tardis_key
read -p "Telegram Bot Token: " telegram_token
read -p "Telegram Chat ID: " chat_id

# Optional
echo ""
echo "📋 Optional configuration (press Enter to skip):"
read -p "Allowed users (comma-separated, e.g., intern,dev): " allowed_users
read -p "API Token (for additional authentication): " api_token

# Update .env file
sed -i "s|TARDIS_API_KEY=.*|TARDIS_API_KEY=$tardis_key|" .env
sed -i "s|TELEGRAM_BOT_TOKEN=.*|TELEGRAM_BOT_TOKEN=$telegram_token|" .env
sed -i "s|TELEGRAM_CHAT_ID=.*|TELEGRAM_CHAT_ID=$chat_id|" .env

if [ ! -z "$allowed_users" ]; then
    sed -i "s|ALLOWED_USERS=.*|ALLOWED_USERS=$allowed_users|" .env
fi

if [ ! -z "$api_token" ]; then
    sed -i "s|API_TOKEN=.*|API_TOKEN=$api_token|" .env
fi

echo ""
echo "✅ Configuration saved to .env"
echo ""

# Create necessary directories
mkdir -p datasets data logs
echo "✅ Created data directories"
echo ""

echo "=========================================="
echo "  Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Review your .env file: nano .env"
echo "2. Start the service: docker-compose up -d"
echo "3. Check logs: docker-compose logs -f"
echo "4. Test the service: curl http://localhost:8000/health"
echo ""
echo "For more information, see README.md"