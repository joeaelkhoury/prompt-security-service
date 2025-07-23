"""Diagnostic script to identify service issues."""

import requests
import json
import time
from datetime import datetime


def test_endpoint(url, name, method="GET", json_data=None, timeout=30):
    """Test a single endpoint and report results."""
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print(f"URL: {url}")
    print(f"Method: {method}")
    if json_data:
        print(f"Payload: {json.dumps(json_data, indent=2)}")
    
    start_time = time.time()
    try:
        if method == "GET":
            response = requests.get(url, timeout=timeout)
        else:
            response = requests.post(url, json=json_data, timeout=timeout)
        
        duration = time.time() - start_time
        
        print(f"\n✅ Success!")
        print(f"Status Code: {response.status_code}")
        print(f"Response Time: {duration:.3f} seconds")
        print(f"Response: {json.dumps(response.json(), indent=2)[:500]}...")
        
        return True, duration
        
    except requests.exceptions.Timeout:
        duration = time.time() - start_time
        print(f"\n❌ TIMEOUT after {duration:.1f} seconds")
        return False, duration
        
    except requests.exceptions.ConnectionError as e:
        print(f"\n❌ CONNECTION ERROR: {e}")
        return False, 0
        
    except Exception as e:
        print(f"\n❌ ERROR: {type(e).__name__}: {e}")
        return False, 0


def diagnose_service(base_url="http://localhost:8000"):
    """Run comprehensive diagnostics on the service."""
    print(f"🔍 PROMPT SECURITY SERVICE DIAGNOSTICS")
    print(f"Time: {datetime.now()}")
    print(f"Base URL: {base_url}")
    
    # Test 1: Basic health check
    test_endpoint(f"{base_url}/health", "Health Check")
    
    # Test 2: Metrics endpoint
    test_endpoint(f"{base_url}/metrics", "Metrics")
    
    # Test 3: Similarity metrics info
    test_endpoint(f"{base_url}/similarity-metrics", "Similarity Metrics")
    
    # Test 4: Simple analyze request (minimal)
    print("\n" + "="*60)
    print("TESTING ANALYZE ENDPOINT WITH DIFFERENT CONFIGURATIONS")
    
    # Test 4a: Minimal request
    minimal_payload = {
        "user_id": "test",
        "prompt1": "Hi",
        "prompt2": "Hello"
    }
    success, duration = test_endpoint(
        f"{base_url}/analyze", 
        "Minimal Analyze Request", 
        "POST", 
        minimal_payload,
        timeout=60  # Longer timeout for analyze
    )
    
    # Test 4b: With specific metric
    if success:
        metric_payload = {
            "user_id": "test",
            "prompt1": "Test",
            "prompt2": "Test",
            "similarity_metric": "jaccard",  # Avoid embedding calculation
            "similarity_threshold": 0.5
        }
        test_endpoint(
            f"{base_url}/analyze", 
            "Analyze with Jaccard (no embeddings)", 
            "POST", 
            metric_payload,
            timeout=30
        )
    
    # Test 5: Check if it's an Azure OpenAI issue
    print("\n" + "="*60)
    print("CHECKING POTENTIAL ISSUES:")
    
    # Check environment
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    print("\n1. Environment Variables:")
    env_vars = [
        "AZURE_OPENAI_API_KEY",
        "AZURE_OPENAI_ENDPOINT",
        "AZURE_OPENAI_CHAT_DEPLOYMENT_NAME",
        "AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME"
    ]
    
    for var in env_vars:
        value = os.getenv(var)
        if value:
            masked = value[:10] + "..." if len(value) > 10 else value
            print(f"   ✅ {var}: {masked}")
        else:
            print(f"   ❌ {var}: NOT SET")
    
    # Test with mock data to bypass Azure
    print("\n2. Testing with mock LLM (to isolate Azure issues):")
    print("   If this works but regular requests don't, the issue is with Azure OpenAI")
    
    # Summary
    print("\n" + "="*60)
    print("DIAGNOSTIC SUMMARY:")
    print("\nPossible issues:")
    print("1. Azure OpenAI connection timeout (most likely)")
    print("   - Check your Azure endpoint is correct")
    print("   - Verify API key is valid")
    print("   - Check if deployments exist in Azure")
    print("\n2. Embedding calculation taking too long")
    print("   - Try using non-embedding similarity metrics")
    print("\n3. Network/firewall issues")
    print("   - Check if you can access Azure OpenAI directly")
    print("\nRecommended actions:")
    print("1. Test Azure OpenAI connection separately")
    print("2. Increase timeout in load test")
    print("3. Use 'jaccard' or 'levenshtein' metrics instead of embeddings")
    print("4. Check service logs for errors")


def test_azure_openai():
    """Test Azure OpenAI connection directly."""
    print("\n" + "="*60)
    print("TESTING AZURE OPENAI DIRECTLY")
    
    from dotenv import load_dotenv
    import os
    load_dotenv()
    
    try:
        from openai import AzureOpenAI
        
        client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )
        
        print("\nTesting chat completion...")
        start = time.time()
        response = client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"),
            messages=[{"role": "user", "content": "Say 'test'"}],
            max_tokens=10
        )
        duration = time.time() - start
        print(f"✅ Chat completion successful in {duration:.2f}s")
        
        print("\nTesting embeddings...")
        start = time.time()
        response = client.embeddings.create(
            model=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME"),
            input="test"
        )
        duration = time.time() - start
        print(f"✅ Embeddings successful in {duration:.2f}s")
        
    except Exception as e:
        print(f"❌ Azure OpenAI Error: {type(e).__name__}: {e}")
        print("\nThis is likely the cause of the timeout!")


if __name__ == "__main__":
    diagnose_service()
    test_azure_openai()