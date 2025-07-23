import requests
import json
import time

API_URL = "http://localhost:8080"

def make_api_call(question):
    print(f"\n{'='*80}")
    print(f"QUESTION: {question}")
    print(f"{'='*80}")
    
    payload = {"question": question}
    print(f"API ENDPOINT: POST {API_URL}/ask")
    print(f"REQUEST BODY:")
    print(json.dumps(payload, indent=2))
    print(f"CONTENT-TYPE: application/json")
    
    start_time = time.time()
    print(f"\nMaking API call... (timestamp: {time.strftime('%H:%M:%S')})")
    
    try:
        response = requests.post(f"{API_URL}/ask", json=payload, timeout=30)
        end_time = time.time()
        
        print(f"Response received in {end_time - start_time:.2f} seconds")
        print(f"\nHTTP RESPONSE:")
        print(f"   Status Code: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('content-type', 'N/A')}")
        print(f"   Response Size: {len(response.content)} bytes")
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"\nSUCCESS - API RESPONSE DATA:")
            print(f"{'─'*60}")
            print(f"AI ANSWER: {result.get('answer', 'No answer provided')}")
            print(f"GENERATED SQL: {result.get('sql_query', 'No SQL generated')}")
            print(f"ROWS RETURNED: {result.get('row_count', 0)}")
            
            if result.get('results') and result['results'].get('data'):
                data = result['results']['data']
                print(f"SAMPLE RESULTS (first 3 rows):")
                for i, row in enumerate(data[:3]):
                    print(f"   Row {i+1}: {row}")
                if len(data) > 3:
                    print(f"   ... and {len(data) - 3} more rows")
            
            print(f"{'─'*60}")
            
        else:
            print(f"\nERROR RESPONSE:")
            print(f"   Status: {response.status_code}")
            print(f"   Error: {response.text}")
            
    except requests.exceptions.Timeout:
        print(f"\nTIMEOUT: API call took longer than 30 seconds")
    except requests.exceptions.ConnectionError:
        print(f"\nCONNECTION ERROR: Could not connect to {API_URL}")
        print(f"   Make sure FastAPI server is running!")
    except Exception as e:
        print(f"\nUNEXPECTED ERROR: {str(e)}")

def check_server_status():
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        if response.status_code == 200:
            result = response.json()
            print(f"Server Status: {result.get('status', 'unknown')}")
            print(f"Agent Status: {result.get('agent', 'unknown')}")
            return True
        else:
            print(f"Server returned status: {response.status_code}")
            return False
    except:
        print(f"FastAPI server not reachable at {API_URL}")
        print(f"   Start server with: python api.py")
        return False

def main():
    print("INTERACTIVE E-COMMERCE AI API TESTER")
    print(f"FastAPI Server: {API_URL}")
    print("="*80)
    
    print("Checking server status...")
    if not check_server_status():
        print("\nPlease start the FastAPI server first!")
        return
    
    print("\nDEMO QUESTIONS (or type your own):")
    demo_questions = [
        "What is my total sales?",
        "Calculate the RoAS (Return on Ad Spend)",
        "Which product had the highest CPC (Cost Per Click)?",
        "Show me top 5 products by revenue",
        "How many products are eligible for advertising?",
        "What is the average cost per click?"
    ]
    
    for i, q in enumerate(demo_questions, 1):
        print(f"   {i}. {q}")
    
    print(f"\nInstructions:")
    print(f"   - Type any question about your e-commerce data")
    print(f"   - Press Enter to send API request")
    print(f"   - Type 'quit' to exit")
    print(f"   - API calls will show LLM responses in real-time")
    
    while True:
        print(f"\n{'─'*80}")
        question = input("Enter your question: ").strip()
        
        if question.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            break
        
        if not question:
            print("Please enter a question")
            continue
        
        make_api_call(question)

if __name__ == "__main__":
    main()
