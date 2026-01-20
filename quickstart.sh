#!/bin/bash

echo "================================================"
echo "  Hyperliquid Tracker - Quick Start"
echo "================================================"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✓ .env file created"
    echo ""
    echo "⚠️  Please edit .env with your configuration before proceeding"
    echo "   (API keys are optional for tracking only)"
    echo ""
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
    echo ""
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt --quiet
echo "✓ Dependencies installed"
echo ""

echo "================================================"
echo "  Setup Complete!"
echo "================================================"
echo ""
echo "What would you like to do?"
echo ""
echo "1. Track top accounts (one-time)"
echo "2. Track top accounts (continuous)"
echo "3. View analytics"
echo "4. Monitor for copy trading (simulation)"
echo "5. Exit"
echo ""
read -p "Enter your choice (1-5): " choice

case $choice in
    1)
        echo ""
        echo "Tracking top accounts..."
        python main.py --mode track
        ;;
    2)
        echo ""
        echo "Starting continuous tracking (Ctrl+C to stop)..."
        python main.py --mode track --continuous
        ;;
    3)
        echo ""
        python main.py --mode analytics --details
        ;;
    4)
        echo ""
        echo "Starting copy trade monitoring (SIMULATION MODE)..."
        echo "Set COPY_TRADE_ENABLED=true in .env to enable actual trading"
        echo ""
        python main.py --mode copytrade --testnet
        ;;
    5)
        echo "Goodbye!"
        exit 0
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac
