import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from onchain_reader import get_onchain_reader
from config import config_loader

async def test_real_positions():
    """Test reading real LP-NFT positions from Base mainnet."""
    
    print("🔍 Testing Real LP-NFT Position Reading")
    print("=" * 50)
    
    try:
        # Load configuration
        config = config_loader.load_config()
        print(f"✅ Config loaded - RPC: {config.blockchain.rpc_url}")
        print(f"✅ Wallet: {config.blockchain.wallet_address}")
        
        # Initialize on-chain reader
        reader = get_onchain_reader(
            config.blockchain.rpc_url,
            config.blockchain.wallet_address
        )
        
        # Test LP-NFT IDs provided by client
        nft_ids = [19542083, 19922090]
        
        print(f"\n📋 Testing LP-NFT IDs: {nft_ids}")
        print("-" * 30)
        
        for nft_id in nft_ids:
            print(f"\n🔍 Reading LP-NFT {nft_id}...")
            try:
                position = await reader._get_single_position(nft_id)
                if position:
                    print(f"✅ Successfully read LP-NFT {nft_id}")
                    print(f"   Pool: {position.pool_address}")
                    print(f"   Token0: {position.token0.symbol} ({position.token0.balance:.6f})")
                    print(f"   Token1: {position.token1.symbol} ({position.token1.balance:.6f})")
                    print(f"   Fee Tier: {position.fee_tier}")
                    print(f"   In Range: {position.in_range}")
                    print(f"   Total Value: ${position.total_usd_value:.2f}")
                    print(f"   Uncollected Fees: {position.uncollected_fees_token0:.6f} {position.token0.symbol}, {position.uncollected_fees_token1:.6f} {position.token1.symbol}")
                else:
                    print(f"❌ Failed to read LP-NFT {nft_id} - Position not found or error")
            except Exception as e:
                print(f"❌ Error reading LP-NFT {nft_id}: {str(e)}")
        
        # Test wallet scanning
        print(f"\n🔍 Testing wallet position scanning...")
        try:
            wallet_positions = await reader.get_wallet_positions()
            print(f"✅ Found {len(wallet_positions)} positions in wallet")
            if wallet_positions:
                print(f"   NFT IDs: {wallet_positions}")
        except Exception as e:
            print(f"❌ Error scanning wallet: {str(e)}")
        
        print("\n" + "=" * 50)
        print("✅ Real position test completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_real_positions()) 