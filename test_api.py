#!/usr/bin/env python3
"""
Test script — verifies the PuterAI Gateway API is working.
Run AFTER starting the server AND opening bridge.html in your browser.

Usage:
  python test_api.py
  python test_api.py --model claude-sonnet-4-6
  python test_api.py --prompt "Write a haiku about Python"
"""
import sys, time, argparse
try:
    from openai import OpenAI
except ImportError:
    print("Installing openai package...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "openai", "-q"])
    from openai import OpenAI

# ── Config ────────────────────────────────────────────────────────────────────
BASE_URL = "https://assembled-viewers-aurora-insider.trycloudflare.com/v1"
API_KEY  = "no-key-needed"   # Puter doesn't need one

def test_models(client):
    print("\n📋 Available models:")
    models = client.models.list()
    for m in models.data:
        print(f"   • {m.id}")

def test_chat(client, model, prompt):
    print(f"\n🤖 Testing: {model}")
    print(f"   Prompt: {prompt}")
    print(f"   Waiting for response ", end="", flush=True)

    t0 = time.time()
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            timeout=90,
        )
        elapsed = time.time() - t0
        content = response.choices[0].message.content
        print(f"({elapsed:.1f}s)")
        print(f"\n   Response:\n   {content[:500]}{'...' if len(content) > 500 else ''}")
        return True
    except Exception as e:
        elapsed = time.time() - t0
        print(f"\n   ❌ Error after {elapsed:.1f}s: {e}")
        return False

def test_multi_turn(client, model):
    print(f"\n🔄 Multi-turn test: {model}")
    messages = []

    # Turn 1
    messages.append({"role": "user", "content": "My name is TestBot. Remember that."})
    print("   Turn 1: Setting name...", end=" ", flush=True)
    r = client.chat.completions.create(model=model, messages=messages, timeout=90)
    reply1 = r.choices[0].message.content
    messages.append({"role": "assistant", "content": reply1})
    print("OK")

    # Turn 2
    messages.append({"role": "user", "content": "What is my name?"})
    print("   Turn 2: Asking name...", end=" ", flush=True)
    r = client.chat.completions.create(model=model, messages=messages, timeout=90)
    reply2 = r.choices[0].message.content
    print(f"Got: '{reply2[:80]}'")

    if "testbot" in reply2.lower():
        print("   ✅ Memory working correctly!")
    else:
        print("   ⚠️  Memory might not be working (model may have forgotten)")

def main():
    parser = argparse.ArgumentParser(description="Test PuterAI Gateway")
    parser.add_argument("--model",  default="claude-sonnet-4-6", help="Model to test")
    parser.add_argument("--prompt", default="Explain what you are in one sentence.")
    parser.add_argument("--all",    action="store_true", help="Test all models")
    args = parser.parse_args()

    client = OpenAI(base_url=BASE_URL, api_key=API_KEY)

    print("═"*55)
    print("  PuterAI Gateway — API Test")
    print(f"  Base URL: {BASE_URL}")
    print("═"*55)
    print("\n⚠️  Make sure bridge.html is open in your browser!\n")

    # Check status
    import urllib.request, json
    try:
        with urllib.request.urlopen("http://localhost:8000/api/status", timeout=3) as r:
            status = json.loads(r.read())
        if status.get("bridge_connected"):
            print("✅ Bridge: CONNECTED")
        else:
            print("❌ Bridge: NOT connected — open bridge.html in your browser first!")
            print("   URL: http://localhost:8000/bridge")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Server not running: {e}")
        print("   Run: bash run.sh")
        sys.exit(1)

    # List models
    test_models(client)

    if args.all:
        models = ["claude-opus-4-7", "claude-sonnet-4-6", "claude-haiku-4-5"]
        for model in models:
            test_chat(client, model, args.prompt)
    else:
        test_chat(client, args.model, args.prompt)
        test_multi_turn(client, args.model)

    print("\n" + "═"*55)
    print("  ✅ Tests complete!")
    print("═"*55 + "\n")

if __name__ == "__main__":
    main()
