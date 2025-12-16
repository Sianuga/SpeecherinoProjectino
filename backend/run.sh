#!/bin/bash
cd "$(dirname "$0")"

# Sprawdź czy venv istnieje
if [ ! -d "venv" ]; then
    echo "Tworzenie środowiska wirtualnego..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

python main.py
