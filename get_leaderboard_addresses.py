#!/usr/bin/env python3
"""
Script to help get Hyperliquid leaderboard addresses from various sources
"""

import requests
from typing import List

def get_hypurrscan_leaderboard() -> List[str]:
    """
    Attempt to get addresses from Hypurrscan (community leaderboard)
    Note: This is an example - the actual endpoint may differ
    """
    addresses = []

    print("Attempting to fetch from Hypurrscan...")
    try:
        # Try the Hypurrscan API (this is speculative - adjust based on actual API)
        response = requests.get("https://api.hypurrscan.io/v1/leaderboard", timeout=10)
        if response.status_code == 200:
            data = response.json()
            # Extract addresses based on response structure
            if isinstance(data, list):
                for item in data:
                    if 'address' in item:
                        addresses.append(item['address'])
                    elif 'user' in item:
                        addresses.append(item['user'])
            print(f"✓ Found {len(addresses)} addresses from Hypurrscan")
        else:
            print(f"❌ Hypurrscan returned status {response.status_code}")
    except Exception as e:
        print(f"❌ Could not fetch from Hypurrscan: {e}")

    return addresses

def get_curated_list() -> List[str]:
    """
    Return a curated list of known high-volume Hyperliquid traders
    These addresses are publicly known from community sources
    """
    # This is a curated list - you should populate with real addresses
    # from Discord, Twitter, or other community sources
    curated = [
        "0x010461C14e146ac35Fe42271BDC1134EE31C703a",  # Example active trader
        # Add more addresses here from community sources
    ]

    print(f"Using curated list of {len(curated)} addresses")
    return curated

def get_addresses_from_file(filename: str) -> List[str]:
    """Read addresses from a text file (one per line)"""
    try:
        with open(filename, 'r') as f:
            addresses = [line.strip() for line in f if line.strip() and line.strip().startswith('0x')]
        print(f"✓ Loaded {len(addresses)} addresses from {filename}")
        return addresses
    except FileNotFoundError:
        print(f"❌ File not found: {filename}")
        return []

def save_addresses_to_file(addresses: List[str], filename: str = 'leaderboard_addresses.txt'):
    """Save addresses to a file"""
    with open(filename, 'w') as f:
        for addr in addresses:
            f.write(f"{addr}\n")
    print(f"✓ Saved {len(addresses)} addresses to {filename}")

def main():
    """Main function"""
    print("="*80)
    print("HYPERLIQUID LEADERBOARD ADDRESS FETCHER")
    print("="*80)

    all_addresses = []

    # Try multiple sources
    print("\n1. Trying Hypurrscan...")
    hypurrscan_addresses = get_hypurrscan_leaderboard()
    all_addresses.extend(hypurrscan_addresses)

    print("\n2. Loading curated list...")
    curated_addresses = get_curated_list()
    all_addresses.extend(curated_addresses)

    # Remove duplicates
    all_addresses = list(set(all_addresses))

    print(f"\n{'='*80}")
    print(f"TOTAL UNIQUE ADDRESSES: {len(all_addresses)}")
    print(f"{'='*80}")

    if all_addresses:
        # Save to file
        save_addresses_to_file(all_addresses)

        print("\nFirst 10 addresses:")
        for i, addr in enumerate(all_addresses[:10], 1):
            print(f"  {i}. {addr}")

        print("\nTo track these addresses, run:")
        print("  python enhanced_tracker.py $(cat leaderboard_addresses.txt | tr '\\n' ' ')")

    else:
        print("\n❌ No addresses found!")
        print("\nManual options:")
        print("1. Create 'leaderboard_addresses.txt' with one address per line")
        print("2. Find addresses from:")
        print("   - Hyperliquid Discord: https://discord.gg/hyperliquid")
        print("   - Community leaderboards")
        print("   - Twitter: Search for #Hyperliquid traders")
        print("   - On-chain explorers")

if __name__ == '__main__':
    main()
