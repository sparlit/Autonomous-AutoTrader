import os

def verify_file(path, required_terms):
    if not os.path.exists(path):
        print(f"❌ {path} missing")
        return False
    with open(path, "r") as f:
        content = f.read()
    for term in required_terms:
        if term not in content:
            print(f"❌ {path} missing required term: {term}")
            return False
    print(f"✅ {path} verified")
    return True

verify_file("src/mql5/Include/AAT_Dashboard.mqh", ["Create", "IsPaused", "OnClick", "Render"])
verify_file("src/mql5/Include/AAT_BridgeClient.mqh", ["Connect", "Send", "Receive", "Disconnect"])
verify_file("src/mql5/Experts/AAT_TradeExecutor.mq5", ["ulong ticket = trade.ResultOrder();", "bridge.Connect"])
