#!/usr/bin/env python3
"""Test script to discover Hyperliquid leaderboard API"""

import requests
import json

# Try different leaderboard endpoints
base_url = "https://api.hyperliquid.xyz"

# Test 1: Try stats-by-user endpoint
print("Testing stats-by-user endpoint...")
try:
    response = requests.post(f"{base_url}/info", json={"type": "statsSpot"})
    print(f"Stats Spot Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Stats Spot Data: {json.dumps(data, indent=2)[:500]}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "="*80 + "\n")

# Test 2: Try user addresses with high volume
print("Testing userStats endpoint...")
test_addresses = [
    "0x010461C14e146ac35Fe42271BDC1134EE31C703a",  # Known active trader
]

for address in test_addresses:
    try:
        response = requests.post(f"{base_url}/info", json={
            "type": "userFills",
            "user": address
        })
        print(f"User {address[:10]}... Status: {response.status_code}")
        if response.status_code == 200:
            fills = response.json()
            print(f"  Total fills: {len(fills) if isinstance(fills, list) else 0}")
            if isinstance(fills, list) and len(fills) > 0:
                print(f"  Recent fill: {fills[0]}")
    except Exception as e:
        print(f"Error: {e}")

print("\n" + "="*80 + "\n")

# Test 3: Try to get global stats
print("Testing globalStats endpoint...")
try:
    response = requests.post(f"{base_url}/info", json={"type": "globalStats"})
    print(f"Global Stats Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Global Stats: {json.dumps(data, indent=2)[:500]}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "="*80 + "\n")

# Test 4: Check available info types
print("Checking meta endpoint for available types...")
try:
    response = requests.post(f"{base_url}/info", json={"type": "meta"})
    print(f"Meta Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Meta data keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "="*80 + "\n")

# Test 5: Try referral stats (might have user data)
print("Testing referral endpoint...")
try:
    response = requests.post(f"{base_url}/info", json={"type": "referral", "user": test_addresses[0]})
    print(f"Referral Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Referral: {json.dumps(data, indent=2)[:500]}")
except Exception as e:
    print(f"Error: {e}")
