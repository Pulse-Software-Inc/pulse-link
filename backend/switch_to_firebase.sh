#!/bin/bash
# mock to real

echo "switch from  PulseLink Mockend to Real Firebase..."

# Check if service account exists
if [ ! -f "firebase-service-account.json" ]; then
    echo " Error firebase-service-account.json not found"
    exit 1


# original backup file
cp app/main.py app/main.py.mock_backup

# to replace mock_db to real db
sed -i 's/app.state.db = mock_db/app.state.db = db/' app/main.py
sed -i 's/app.state.use_mock = True/app.state.use_mock = False/' app/main.py

echo "switched to real db"
