#!/usr/bin/env python3
"""
Test script to find working Base RPC endpoints
"""

import asyncio
import aiohttp
import json
from web3 import Web3

# Public Base RPC endpoints to test
RPC_ENDPOINTS = [
    "https://mainnet.base.org",
    "https://base.blockpi.network/v1/rpc/public",
    "https://1rpc.io/base",
    "https://base.meowrpc.com",
    "https://base.drpc.org",
    "https://base-rpc.publicnode.com",
    "https://base.llamarpc.com"
]

async def test_rpc_endpoint(url):
    """Test if an RPC endpoint is working."""
    try:
        async with aiohttp.ClientSession() as session:
            payload = {
                "jsonrpc": "2.0",
                "method": "eth_blockNumber",
                "params": [],
                "id": 1
            }
            
            async with session.post(url, json=payload, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    if 'result' in data:
                        block_number = int(data['result'], 16)
                        return True, block_number
                    else:
                        return False, f"Invalid response: {data}"
                else:
                    return False, f"HTTP {response.status}"
    except Exception as e:
        return False, str(e)

async def test_all_rpcs():
    """Test all RPC endpoints."""
    print("🔍 Testing Base RPC Endpoints")
    print("=" * 50)
    
    working_endpoints = []
    
    for url in RPC_ENDPOINTS:
        print(f"\nTesting: {url}")
        success, result = await test_rpc_endpoint(url)
        
        if success:
            print(f"✅ Working - Block #{result:,}")
            working_endpoints.append((url, result))
        else:
            print(f"❌ Failed - {result}")
    
    return working_endpoints

def test_web3_connection(url):
    """Test Web3 connection to an endpoint."""
    try:
        w3 = Web3(Web3.HTTPProvider(url))
        if w3.is_connected():
            block_number = w3.eth.block_number
            return True, block_number
        else:
            return False, "Not connected"
    except Exception as e:
        return False, str(e)

async def main():
    """Main test function."""
    print("Testing HTTP endpoints...")
    working_http = await test_all_rpcs()
    
    print("\n" + "=" * 50)
    print("Testing Web3 connections...")
    
    for url, block_num in working_http:
        print(f"\nTesting Web3: {url}")
        success, result = test_web3_connection(url)
        
        if success:
            print(f"✅ Web3 Working - Block #{result:,}")
        else:
            print(f"❌ Web3 Failed - {result}")
    
    print("\n" + "=" * 50)
    print("📋 Summary of Working Endpoints:")
    
    for url, block_num in working_http:
        print(f"✅ {url}")
    
    if working_http:
        print(f"\n🎯 Recommended for testing: {working_http[0][0]}")
    else:
        print("\n❌ No working endpoints found")

if __name__ == "__main__":
    asyncio.run(main()) 