"""
Test all API keys to verify they work
"""
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_gemini_api():
    """Test Gemini API"""
    try:
        import google.genai as genai
        api_key = os.getenv("GEMINI_API_KEY")
        
        if not api_key:
            return "❌ GEMINI: API key not configured"
        
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model='gemini-2.0-flash-exp',
            contents='Say hello'
        )
        
        return f"✅ GEMINI: Working! Response: {response.text[:50]}..."
    except Exception as e:
        return f"❌ GEMINI: Failed - {str(e)[:100]}"

async def test_qwen_api():
    """Test Qwen API"""
    try:
        import httpx
        api_key = os.getenv("QWEN_API_KEY")
        
        if not api_key:
            return "❌ QWEN: API key not configured"
        
        url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "qwen-plus",
            "messages": [{"role": "user", "content": "Say hello"}],
            "max_tokens": 10
        }
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, json=data, headers=headers)
            
        if response.status_code == 200:
            return f"✅ QWEN: Working! Status: {response.status_code}"
        else:
            return f"❌ QWEN: Failed - Status {response.status_code}: {response.text[:100]}"
    except Exception as e:
        return f"❌ QWEN: Failed - {str(e)[:100]}"

async def test_mistral_api():
    """Test Mistral API"""
    try:
        import httpx
        api_key = os.getenv("MISTRAL_API_KEY")
        
        if not api_key:
            return "❌ MISTRAL: API key not configured"
        
        url = "https://api.mistral.ai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "mistral-small-latest",
            "messages": [{"role": "user", "content": "Say hello"}],
            "max_tokens": 10
        }
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, json=data, headers=headers)
            
        if response.status_code == 200:
            return f"✅ MISTRAL: Working! Status: {response.status_code}"
        else:
            return f"❌ MISTRAL: Failed - Status {response.status_code}: {response.text[:100]}"
    except Exception as e:
        return f"❌ MISTRAL: Failed - {str(e)[:100]}"

async def test_tavily_api():
    """Test Tavily Search API"""
    try:
        import httpx
        api_key = os.getenv("TAVILY_API_KEY")
        
        if not api_key:
            return "❌ TAVILY: API key not configured"
        
        url = "https://api.tavily.com/search"
        data = {
            "api_key": api_key,
            "query": "test",
            "max_results": 1
        }
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, json=data)
            
        if response.status_code == 200:
            return f"✅ TAVILY: Working! Status: {response.status_code}"
        else:
            return f"❌ TAVILY: Failed - Status {response.status_code}: {response.text[:100]}"
    except Exception as e:
        return f"❌ TAVILY: Failed - {str(e)[:100]}"

async def test_openweather_api():
    """Test OpenWeather API"""
    try:
        import httpx
        api_key = os.getenv("OPENWEATHER_API_KEY")
        
        if not api_key:
            return "❌ OPENWEATHER: API key not configured"
        
        url = f"https://api.openweathermap.org/data/2.5/weather?q=Colombo&appid={api_key}"
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            
        if response.status_code == 200:
            return f"✅ OPENWEATHER: Working! Status: {response.status_code}"
        else:
            return f"❌ OPENWEATHER: Failed - Status {response.status_code}: {response.text[:100]}"
    except Exception as e:
        return f"❌ OPENWEATHER: Failed - {str(e)[:100]}"

async def test_currencylayer_api():
    """Test CurrencyLayer API"""
    try:
        import httpx
        api_key = os.getenv("CURRENCYLAYER_API_KEY")
        
        if not api_key:
            return "❌ CURRENCYLAYER: API key not configured"
        
        url = f"http://api.currencylayer.com/live?access_key={api_key}&currencies=USD&source=USD&format=1"
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                return f"✅ CURRENCYLAYER: Working! Status: {response.status_code}"
            else:
                return f"❌ CURRENCYLAYER: API Error - {data.get('error', {}).get('info', 'Unknown error')}"
        else:
            return f"❌ CURRENCYLAYER: Failed - Status {response.status_code}"
    except Exception as e:
        return f"❌ CURRENCYLAYER: Failed - {str(e)[:100]}"

async def test_google_maps_api():
    """Test Google Maps API"""
    try:
        import httpx
        api_key = os.getenv("GOOGLE_MAPS_API_KEY")
        
        if not api_key:
            return "❌ GOOGLE_MAPS: API key not configured"
        
        url = f"https://maps.googleapis.com/maps/api/geocode/json?address=Colombo&key={api_key}"
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "OK":
                return f"✅ GOOGLE_MAPS: Working! Status: {data['status']}"
            else:
                return f"❌ GOOGLE_MAPS: API Error - {data.get('status', 'Unknown')}"
        else:
            return f"❌ GOOGLE_MAPS: Failed - Status {response.status_code}"
    except Exception as e:
        return f"❌ GOOGLE_MAPS: Failed - {str(e)[:100]}"

async def main():
    """Run all API tests"""
    print("=" * 70)
    print("API KEY VALIDATION TEST")
    print("=" * 70)
    print()
    
    # Run all tests
    results = await asyncio.gather(
        test_gemini_api(),
        test_qwen_api(),
        test_mistral_api(),
        test_tavily_api(),
        test_openweather_api(),
        test_currencylayer_api(),
        test_google_maps_api()
    )
    
    # Print results
    for result in results:
        print(result)
    
    print()
    print("=" * 70)
    
    # Count successes
    success_count = sum(1 for r in results if r.startswith("✅"))
    total_count = len(results)
    
    print(f"SUMMARY: {success_count}/{total_count} APIs working correctly")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(main())
