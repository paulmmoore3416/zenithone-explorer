"""
ZenithOne Explorer - Load Testing
Performance tests for concurrent workload handling
"""

import pytest
import requests
import time
import concurrent.futures
from statistics import mean, median, stdev
import json


BASE_URL = "http://localhost:8000/api/v1"
AUTH_TOKEN = None


@pytest.fixture(scope="module", autouse=True)
def setup_auth():
    """Authenticate before running load tests"""
    global AUTH_TOKEN
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"username": "admin", "password": "admin123"}
    )
    if response.status_code == 200:
        AUTH_TOKEN = response.json().get("access_token")


def get_headers():
    """Get authentication headers"""
    return {"Authorization": f"Bearer {AUTH_TOKEN}"}


class TestConcurrentWorkloads:
    """Test concurrent workload creation and management"""
    
    @pytest.mark.performance
    def test_concurrent_workload_creation(self):
        """Test creating 100 workloads concurrently"""
        num_workloads = 100
        results = []
        
        def create_workload(index):
            start_time = time.time()
            try:
                response = requests.post(
                    f"{BASE_URL}/workloads",
                    json={
                        "name": f"load-test-{index}",
                        "type": "batch",
                        "image": "alpine:latest",
                        "command": "echo 'test'",
                        "priority": "normal"
                    },
                    headers=get_headers(),
                    timeout=30
                )
                elapsed = time.time() - start_time
                return {
                    "success": response.status_code == 201,
                    "status_code": response.status_code,
                    "elapsed": elapsed
                }
            except Exception as e:
                elapsed = time.time() - start_time
                return {
                    "success": False,
                    "error": str(e),
                    "elapsed": elapsed
                }
        
        # Execute concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(create_workload, i) for i in range(num_workloads)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        # Analyze results
        successful = [r for r in results if r["success"]]
        failed = [r for r in results if not r["success"]]
        response_times = [r["elapsed"] for r in results]
        
        # Assertions
        success_rate = len(successful) / num_workloads * 100
        assert success_rate >= 95, f"Success rate {success_rate}% is below 95%"
        
        avg_response_time = mean(response_times)
        assert avg_response_time < 2.0, f"Average response time {avg_response_time}s exceeds 2s"
        
        # Print statistics
        print(f"\n=== Load Test Results ===")
        print(f"Total Requests: {num_workloads}")
        print(f"Successful: {len(successful)} ({success_rate:.2f}%)")
        print(f"Failed: {len(failed)}")
        print(f"Avg Response Time: {avg_response_time:.3f}s")
        print(f"Median Response Time: {median(response_times):.3f}s")
        print(f"Std Dev: {stdev(response_times):.3f}s")
        print(f"Min: {min(response_times):.3f}s")
        print(f"Max: {max(response_times):.3f}s")
    
    @pytest.mark.performance
    def test_concurrent_workload_listing(self):
        """Test listing workloads under concurrent load"""
        num_requests = 50
        results = []
        
        def list_workloads():
            start_time = time.time()
            try:
                response = requests.get(
                    f"{BASE_URL}/workloads",
                    headers=get_headers(),
                    timeout=10
                )
                elapsed = time.time() - start_time
                return {
                    "success": response.status_code == 200,
                    "elapsed": elapsed,
                    "count": len(response.json()) if response.status_code == 200 else 0
                }
            except Exception as e:
                elapsed = time.time() - start_time
                return {
                    "success": False,
                    "elapsed": elapsed,
                    "error": str(e)
                }
        
        # Execute concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(list_workloads) for _ in range(num_requests)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        # Analyze results
        successful = [r for r in results if r["success"]]
        response_times = [r["elapsed"] for r in results]
        
        success_rate = len(successful) / num_requests * 100
        assert success_rate >= 98, f"Success rate {success_rate}% is below 98%"
        
        avg_response_time = mean(response_times)
        assert avg_response_time < 1.0, f"Average response time {avg_response_time}s exceeds 1s"


class TestAPIThroughput:
    """Test API throughput and response times"""
    
    @pytest.mark.performance
    def test_api_throughput(self):
        """Test API requests per second"""
        duration = 10  # seconds
        results = []
        
        def make_request():
            start_time = time.time()
            try:
                response = requests.get(
                    f"{BASE_URL}/metrics",
                    headers=get_headers(),
                    timeout=5
                )
                elapsed = time.time() - start_time
                return {
                    "success": response.status_code == 200,
                    "elapsed": elapsed
                }
            except:
                return {"success": False, "elapsed": 0}
        
        # Run requests for specified duration
        start_time = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            while time.time() - start_time < duration:
                futures.append(executor.submit(make_request))
            
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        # Calculate throughput
        total_requests = len(results)
        successful_requests = len([r for r in results if r["success"]])
        requests_per_second = total_requests / duration
        
        print(f"\n=== Throughput Test Results ===")
        print(f"Duration: {duration}s")
        print(f"Total Requests: {total_requests}")
        print(f"Successful: {successful_requests}")
        print(f"Throughput: {requests_per_second:.2f} req/s")
        
        assert requests_per_second >= 50, f"Throughput {requests_per_second} req/s is below 50 req/s"


class TestDatabasePerformance:
    """Test database query performance under load"""
    
    @pytest.mark.performance
    @pytest.mark.slow
    def test_database_query_performance(self):
        """Test database performance with large dataset"""
        # Create multiple workloads first
        num_workloads = 50
        
        for i in range(num_workloads):
            requests.post(
                f"{BASE_URL}/workloads",
                json={
                    "name": f"db-perf-test-{i}",
                    "type": "batch",
                    "image": "alpine:latest",
                    "command": "echo 'test'"
                },
                headers=get_headers()
            )
        
        # Test query performance
        start_time = time.time()
        response = requests.get(f"{BASE_URL}/workloads", headers=get_headers())
        query_time = time.time() - start_time
        
        assert response.status_code == 200
        assert query_time < 1.0, f"Query time {query_time}s exceeds 1s"
        
        print(f"\n=== Database Query Performance ===")
        print(f"Workloads in DB: {len(response.json())}")
        print(f"Query Time: {query_time:.3f}s")


class TestMemoryUsage:
    """Test memory usage under load"""
    
    @pytest.mark.performance
    def test_memory_stability(self):
        """Test that memory usage remains stable under load"""
        # Get initial memory usage
        initial_metrics = requests.get(f"{BASE_URL}/metrics", headers=get_headers())
        initial_memory = initial_metrics.json().get("memory", {}).get("current", 0)
        
        # Create load
        for i in range(100):
            requests.post(
                f"{BASE_URL}/workloads",
                json={
                    "name": f"memory-test-{i}",
                    "type": "batch",
                    "image": "alpine:latest",
                    "command": "echo 'test'"
                },
                headers=get_headers()
            )
        
        # Get final memory usage
        final_metrics = requests.get(f"{BASE_URL}/metrics", headers=get_headers())
        final_memory = final_metrics.json().get("memory", {}).get("current", 0)
        
        memory_increase = final_memory - initial_memory
        
        print(f"\n=== Memory Usage Test ===")
        print(f"Initial Memory: {initial_memory:.2f}%")
        print(f"Final Memory: {final_memory:.2f}%")
        print(f"Increase: {memory_increase:.2f}%")
        
        # Memory should not increase by more than 20%
        assert memory_increase < 20, f"Memory increased by {memory_increase}%, exceeds 20%"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s", "-m", "performance"])
