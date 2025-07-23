import asyncio
import aiohttp
import time
import json
import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import random

# Import test scenarios
from test_prompts import TestPrompts


@dataclass
class TestResult:
    """Result of a single test."""
    test_name: str
    category: str
    duration: float
    success: bool
    expected_blocked: bool
    actually_blocked: bool
    has_llm_response: bool
    explanation: str
    similarity_scores: Optional[Dict[str, float]] = None
    error: Optional[str] = None
    
    @property
    def test_passed(self) -> bool:
        """Test passes if blocking behavior matches expectation."""
        return self.success and (self.expected_blocked == self.actually_blocked)


class LoadTester:
    """Load testing framework."""
    
    def __init__(self, base_url: str = None):
        # Check environment variable first, then try to auto-detect
        if base_url:
            self.base_url = base_url
        else:
            self.base_url = self._detect_base_url()
        
        self.results: List[TestResult] = []
        self.start_time = None
        self.end_time = None
    
    def _detect_base_url(self) -> str:
        """Auto-detect the correct base URL."""
        import requests
        
        # Try common endpoints in order
        endpoints = [
            "http://localhost",        # Docker with Nginx
            "http://localhost:80",     # Explicit port 80
            "http://localhost:8000",   # Direct API
            "http://127.0.0.1",       # Alternative localhost
            "http://host.docker.internal:8000",  # From inside Docker
        ]
        
        # Check environment variable
        if os.getenv("API_BASE"):
            endpoints.insert(0, os.getenv("API_BASE"))
        
        for endpoint in endpoints:
            try:
                resp = requests.get(f"{endpoint}/health", timeout=2)
                if resp.status_code == 200:
                    print(f"✅ Found service at: {endpoint}")
                    return endpoint
            except:
                continue
        
        # Default fallback
        return "http://localhost"
    
    async def execute_test(
        self, 
        session: aiohttp.ClientSession,
        test_case: Dict[str, Any],
        user_id: str = None
    ) -> TestResult:
        """Execute a single test case."""
        start = time.time()
        
        # Build request payload
        payload = {
            "user_id": user_id or f"test_user_{random.randint(1000, 9999)}",
            "prompt1": test_case["prompt1"],
            "prompt2": test_case["prompt2"],
            "similarity_metric": test_case.get("similarity_metric", "cosine"),
            "similarity_threshold": test_case.get("similarity_threshold", 0.7)
        }
        
        try:
            timeout = aiohttp.ClientTimeout(total=30)
            async with session.post(
                f"{self.base_url}/analyze",
                json=payload,
                timeout=timeout
            ) as response:
                data = await response.json()
                duration = time.time() - start
                
                # FIXED LOGIC: Analyze response to determine if attack was actually blocked
                explanation = data.get("explanation", "").lower()
                
                # Check for specific indicators of success vs blocking
                if "no security issues detected" in explanation:
                    # This means the request was successful, not blocked
                    actually_blocked = False
                elif data.get("llm_response") is None and test_case.get("expected_blocked", False):
                    # No LLM response when we expected blocking = correctly blocked
                    actually_blocked = True
                else:
                    # Look for specific blocking indicators
                    actually_blocked = any([
                        "has been blocked" in explanation,
                        "blocked due to" in explanation,
                        "agents recommended blocking" in explanation,
                        "security issues detected:" in explanation,  # Note the colon
                        "sql injection detected" in explanation,
                        "xss attack detected" in explanation,
                        "prompt injection detected" in explanation,
                        "data exfiltration detected" in explanation,
                        # Check if multiple agents voted to block
                        any(
                            agent.get('recommendation') == 'block' 
                            for agent in data.get('agent_findings', [])
                        ),
                        # No LLM response for non-attack queries indicates blocking
                        (data.get("llm_response") is None and not test_case.get("expected_blocked", False))
                    ])
                
                # Additional validation: if success=True and llm_response exists, it's not blocked
                if data.get("success", False) and data.get("llm_response") is not None:
                    # Unless there's explicit blocking language
                    if not any(phrase in explanation for phrase in ["blocked", "detected", "malicious"]):
                        actually_blocked = False
                
                return TestResult(
                    test_name=test_case["name"],
                    category=test_case.get("category", "unknown"),
                    duration=duration,
                    success=data.get("success", False),
                    expected_blocked=test_case.get("expected_blocked", False),
                    actually_blocked=actually_blocked,
                    has_llm_response=data.get("llm_response") is not None,
                    explanation=data.get("explanation", ""),
                    similarity_scores=data.get("similarity_scores", {})
                )
                
        except Exception as e:
            return TestResult(
                test_name=test_case["name"],
                category=test_case.get("category", "unknown"),
                duration=time.time() - start,
                success=False,
                expected_blocked=test_case.get("expected_blocked", False),
                actually_blocked=False,
                has_llm_response=False,
                explanation="",
                error=str(e)
            )
    
    async def run_security_tests(self, concurrent: int = 3):
        """Run all security-focused tests."""
        print("\n🔒 SECURITY TESTING SUITE (P2SQL INJECTION PATTERNS)")
        print("=" * 70)
        print("Testing sophisticated attack vectors from P2SQL research\n")
        
        self.start_time = time.time()
        
        # Get all attack scenarios
        attacks = TestPrompts.get_all_attacks()
        legitimate = TestPrompts.get_legitimate_queries()
        all_tests = attacks + legitimate
        
        # Shuffle to mix attack and legitimate queries
        random.shuffle(all_tests)
        
        # Execute tests with controlled concurrency
        semaphore = asyncio.Semaphore(concurrent)
        
        async def bounded_test(session, test_case, index):
            async with semaphore:
                print(f"[{index+1}/{len(all_tests)}] Testing: {test_case['name'][:50]}...", end="", flush=True)
                result = await self.execute_test(session, test_case)
                
                # Print immediate result
                if result.test_passed:
                    print(f" ✅ ({result.duration:.2f}s)")
                else:
                    if result.success:
                        print(f" ❌ FAILED - Expected block={result.expected_blocked}, Got={result.actually_blocked} ({result.duration:.2f}s)")
                    else:
                        print(f" ❌ ERROR - {result.error}")
                
                return result
        
        async with aiohttp.ClientSession() as session:
            tasks = [bounded_test(session, test, i) for i, test in enumerate(all_tests)]
            self.results = await asyncio.gather(*tasks)
        
        self.end_time = time.time()
        self._print_security_report()
    
    async def run_similarity_tests(self):
        """Test similarity metrics with security-aware pairs."""
        print("\n🔍 SIMILARITY METRIC SECURITY TESTS")
        print("=" * 70)
        print("Testing how similarity metrics handle malicious vs legitimate queries\n")
        
        test_pairs = TestPrompts.get_similarity_test_pairs()
        
        async with aiohttp.ClientSession() as session:
            for i, test in enumerate(test_pairs):
                print(f"[{i+1}/{len(test_pairs)}] {test['name']}:")
                print(f"  Prompt 1: {test['prompt1'][:60]}...")
                print(f"  Prompt 2: {test['prompt2'][:60]}...")
                
                result = await self.execute_test(session, test)
                
                if result.similarity_scores:
                    metric = test.get("similarity_metric", "cosine")
                    score = result.similarity_scores.get(metric, 0)
                    threshold = test.get("similarity_threshold", 0.7)
                    
                    print(f"  {metric.capitalize()} Score: {score:.3f} (threshold: {threshold})")
                    print(f"  Is Similar: {score >= threshold}")
                    print(f"  Blocked: {result.actually_blocked}")
                    print(f"  Explanation: {result.explanation[:100]}...\n")
    
    async def run_stress_test(self, total_requests: int = 100, concurrent: int = 10):
        """Run stress test with mixed workload."""
        print("\n⚡ STRESS TEST")
        print("=" * 70)
        print(f"Running {total_requests} requests with {concurrent} concurrent connections\n")
        
        # Create mixed workload
        attacks = TestPrompts.get_all_attacks()
        legitimate = TestPrompts.get_legitimate_queries()
        
        workload = []
        for i in range(total_requests):
            if i % 3 == 0:  # 33% attacks
                workload.append(random.choice(attacks))
            else:  # 67% legitimate
                workload.append(random.choice(legitimate))
        
        semaphore = asyncio.Semaphore(concurrent)
        progress_counter = 0
        
        async def stress_request(session, test_case, index):
            nonlocal progress_counter
            async with semaphore:
                result = await self.execute_test(session, test_case, f"stress_user_{index % 20}")
                progress_counter += 1
                if progress_counter % 10 == 0:
                    print(f"Progress: {progress_counter}/{total_requests} requests completed")
                return result
        
        start_time = time.time()
        
        async with aiohttp.ClientSession() as session:
            tasks = [stress_request(session, test, i) for i, test in enumerate(workload)]
            results = await asyncio.gather(*tasks)
        
        total_time = time.time() - start_time
        
        # Analyze stress test results
        successful = [r for r in results if r.success]
        blocked = [r for r in successful if r.actually_blocked]
        attacks_in_workload = sum(1 for t in workload if t.get("expected_blocked", False))
        legitimate_in_workload = len(workload) - attacks_in_workload
        
        # Calculate accurate metrics
        true_positives = sum(1 for r in successful if r.expected_blocked and r.actually_blocked)
        false_positives = sum(1 for r in successful if not r.expected_blocked and r.actually_blocked)
        true_negatives = sum(1 for r in successful if not r.expected_blocked and not r.actually_blocked)
        false_negatives = sum(1 for r in successful if r.expected_blocked and not r.actually_blocked)
        
        print(f"\n📊 Stress Test Results:")
        print(f"  Total Time: {total_time:.2f}s")
        print(f"  Throughput: {len(successful)/total_time:.2f} req/s")
        print(f"  Success Rate: {len(successful)/len(results)*100:.1f}%")
        print(f"\n  Workload Composition:")
        print(f"    Attacks: {attacks_in_workload}")
        print(f"    Legitimate: {legitimate_in_workload}")
        print(f"\n  Detection Results:")
        print(f"    True Positives (attacks blocked): {true_positives}")
        print(f"    True Negatives (legitimate allowed): {true_negatives}")
        print(f"    False Positives (legitimate blocked): {false_positives}")
        print(f"    False Negatives (attacks allowed): {false_negatives}")
        
        if attacks_in_workload > 0:
            print(f"\n  Detection Rate: {true_positives/attacks_in_workload*100:.1f}%")
        if legitimate_in_workload > 0:
            print(f"  False Positive Rate: {false_positives/legitimate_in_workload*100:.1f}%")
    
    def _print_security_report(self):
        """Print comprehensive security test report."""
        print("\n" + "=" * 70)
        print("📊 SECURITY TEST REPORT")
        print("=" * 70)
        
        # Group results by category
        categories = {}
        for result in self.results:
            cat = result.category
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(result)
        
        # Print category summaries
        print("\nResults by Attack Category:")
        for category, results in sorted(categories.items()):
            total = len(results)
            passed = sum(1 for r in results if r.test_passed)
            blocked = sum(1 for r in results if r.actually_blocked)
            
            print(f"\n{category.replace('_', ' ').title()}:")
            print(f"  Total Tests: {total}")
            print(f"  Tests Passed: {passed}/{total} ({passed/total*100:.1f}%)")
            
            # Separate attack vs legitimate stats
            attacks = [r for r in results if r.expected_blocked]
            legitimate = [r for r in results if not r.expected_blocked]
            
            if attacks:
                attacks_blocked = sum(1 for r in attacks if r.actually_blocked)
                print(f"  Attacks Blocked: {attacks_blocked}/{len(attacks)} ({attacks_blocked/len(attacks)*100:.1f}%)")
            
            if legitimate:
                legitimate_allowed = sum(1 for r in legitimate if not r.actually_blocked)
                print(f"  Legitimate Allowed: {legitimate_allowed}/{len(legitimate)} ({legitimate_allowed/len(legitimate)*100:.1f}%)")
            
            # Show failed tests with more detail
            failed = [r for r in results if not r.test_passed]
            if failed:
                print(f"  Failed Tests:")
                for f in failed[:5]:  # Show first 5
                    print(f"    - {f.test_name}:")
                    print(f"      Expected: {'Block' if f.expected_blocked else 'Allow'}")
                    print(f"      Got: {'Blocked' if f.actually_blocked else 'Allowed'}")
                    if f.explanation:
                        print(f"      Reason: {f.explanation[:80]}...")
        
        # Overall statistics
        total_tests = len(self.results)
        total_passed = sum(1 for r in self.results if r.test_passed)
        
        # Separate attacks and legitimate queries
        all_attacks = [r for r in self.results if r.expected_blocked]
        all_legitimate = [r for r in self.results if not r.expected_blocked]
        
        attacks_blocked = sum(1 for r in all_attacks if r.actually_blocked)
        legitimate_allowed = sum(1 for r in all_legitimate if not r.actually_blocked)
        
        print(f"\n📈 Overall Statistics:")
        print(f"  Total Tests: {total_tests}")
        print(f"  Tests Passed: {total_passed}/{total_tests} ({total_passed/total_tests*100:.1f}%)")
        
        if all_attacks:
            print(f"\n  Attack Detection:")
            print(f"    Total Attacks: {len(all_attacks)}")
            print(f"    Attacks Blocked: {attacks_blocked}/{len(all_attacks)} ({attacks_blocked/len(all_attacks)*100:.1f}%)")
        
        if all_legitimate:
            print(f"\n  Legitimate Query Handling:")
            print(f"    Total Legitimate: {len(all_legitimate)}")
            print(f"    Legitimate Allowed: {legitimate_allowed}/{len(all_legitimate)} ({legitimate_allowed/len(all_legitimate)*100:.1f}%)")
        
        print(f"\n  Total Execution Time: {self.end_time - self.start_time:.2f}s")
        
        # Performance analysis
        durations = [r.duration for r in self.results if r.success]
        if durations:
            print(f"\n⏱️  Performance Metrics:")
            print(f"  Average Response: {sum(durations)/len(durations):.2f}s")
            print(f"  Min/Max: {min(durations):.2f}s / {max(durations):.2f}s")
            
            fast = sum(1 for d in durations if d < 3)
            medium = sum(1 for d in durations if 3 <= d < 10)
            slow = sum(1 for d in durations if d >= 10)
            print(f"  Response Distribution:")
            print(f"    Fast (<3s): {fast} ({fast/len(durations)*100:.1f}%)")
            print(f"    Medium (3-10s): {medium} ({medium/len(durations)*100:.1f}%)")
            print(f"    Slow (>10s): {slow} ({slow/len(durations)*100:.1f}%)")


async def main():
    """Main test execution."""
    import sys
    
    # Create tester instance (will auto-detect base URL)
    tester = LoadTester()
    
    # Check service health
    print("🏥 Checking service health...")
    try:
        import requests
        resp = requests.get(f"{tester.base_url}/health", timeout=3)
        if resp.status_code == 200:
            print("✅ Service is healthy")
            print(f"📍 Using endpoint: {tester.base_url}\n")
        else:
            print(f"❌ Service returned non-200 status: {resp.status_code}")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Cannot connect to service: {e}")
        print("\n🔧 Troubleshooting:")
        print("   1. Make sure Docker services are running:")
        print("      docker-compose up -d")
        print("   2. Wait for services to be ready:")
        print("      docker-compose ps")
        print("   3. Check if the service is accessible:")
        print("      curl http://localhost/health")
        print("\n   If running locally without Docker:")
        print("      python -m src.main")
        sys.exit(1)
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        mode = sys.argv[1]
        
        if mode == "security":
            await tester.run_security_tests()
        elif mode == "similarity":
            await tester.run_similarity_tests()
        elif mode == "stress":
            requests = int(sys.argv[2]) if len(sys.argv) > 2 else 100
            concurrent = int(sys.argv[3]) if len(sys.argv) > 3 else 10
            await tester.run_stress_test(requests, concurrent)
        elif mode == "all":
            await tester.run_security_tests()
            await tester.run_similarity_tests()
            await tester.run_stress_test(50, 5)
        else:
            print(f"Unknown mode: {mode}")
            print_usage()
    else:
        # Default: run security tests
        await tester.run_security_tests()


def print_usage():
    """Print usage information."""
    print("\nUsage:")
    print("  python tests/test_load.py [mode] [options]")
    print("\nModes:")
    print("  security    - Run P2SQL injection security tests (default)")
    print("  similarity  - Test similarity metrics with malicious pairs")
    print("  stress [requests] [concurrent] - Run stress test")
    print("  all         - Run all test suites")
    print("\nExamples:")
    print("  python tests/test_load.py security")
    print("  python tests/test_load.py stress 200 20")
    print("  python tests/test_load.py all")
    print("\nEnvironment Variables:")
    print("  API_BASE    - Override API endpoint (e.g., http://localhost)")


if __name__ == "__main__":
    asyncio.run(main())
