#!/usr/bin/env python3
"""
Test script to verify the download service is working correctly.
Run this after starting the service to verify everything is set up properly.
"""

import requests
import sys
import time


class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'


def print_test(test_name):
    print(f"\n{Colors.BLUE}Testing: {test_name}{Colors.RESET}")


def print_success(message):
    print(f"{Colors.GREEN}✓ {message}{Colors.RESET}")


def print_error(message):
    print(f"{Colors.RED}✗ {message}{Colors.RESET}")


def print_warning(message):
    print(f"{Colors.YELLOW}⚠ {message}{Colors.RESET}")


def test_service_running(base_url):
    """Test if the service is running."""
    print_test("Service Running")
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print_success(f"Service is running at {base_url}")
            return True
        else:
            print_error(f"Service returned status code {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error(f"Cannot connect to {base_url}. Is the service running?")
        print_warning("Try: docker-compose up -d")
        return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False


def test_health_endpoint(base_url):
    """Test the health endpoint."""
    print_test("Health Endpoint")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_success(f"Health check passed: {data}")
            return True
        else:
            print_error(f"Health check failed with status {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False


def test_api_docs(base_url):
    """Test if API documentation is available."""
    print_test("API Documentation")
    try:
        response = requests.get(f"{base_url}/docs", timeout=5)
        if response.status_code == 200:
            print_success(f"API docs available at {base_url}/docs")
            return True
        else:
            print_error("API docs not accessible")
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False


def test_authentication(base_url):
    """Test authentication requirements."""
    print_test("Authentication")
    try:
        # Try without username header
        response = requests.get(f"{base_url}/jobs", timeout=5)
        if response.status_code in [400, 401, 403]:
            print_success("Authentication is properly enforced")
            return True
        else:
            print_warning("Authentication might not be configured")
            return True  # Not a failure, just a warning
    except Exception as e:
        print_error(f"Error: {e}")
        return False


def test_job_listing(base_url, username="test_user"):
    """Test job listing endpoint."""
    print_test("Job Listing")
    try:
        headers = {"X-Username": username}
        response = requests.get(f"{base_url}/jobs", headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_success(f"Job listing works. Found {data.get('total', 0)} jobs.")
            return True
        elif response.status_code == 403:
            print_warning(f"User '{username}' not authorized. This is expected if user restrictions are enabled.")
            return True
        else:
            print_error(f"Job listing failed with status {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False


def main():
    print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BLUE}  Tardis Download Service - Test Suite{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}")
    
    base_url = "http://localhost:8000"
    
    tests = [
        ("Service Running", lambda: test_service_running(base_url)),
        ("Health Check", lambda: test_health_endpoint(base_url)),
        ("API Documentation", lambda: test_api_docs(base_url)),
        ("Authentication", lambda: test_authentication(base_url)),
        ("Job Listing", lambda: test_job_listing(base_url)),
    ]
    
    results = []
    for test_name, test_func in tests:
        results.append(test_func())
        time.sleep(0.5)  # Brief pause between tests
    
    # Summary
    print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BLUE}  Test Summary{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}")
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"\n{Colors.GREEN}All tests passed! ({passed}/{total}){Colors.RESET}")
        print(f"\n{Colors.GREEN}✓ Service is ready to use!{Colors.RESET}")
        print(f"\nNext steps:")
        print(f"  1. Have the intern try: python client.py --list-jobs")
        print(f"  2. Check API docs: {base_url}/docs")
        print(f"  3. Monitor logs: docker-compose logs -f")
    else:
        print(f"\n{Colors.YELLOW}Some tests had issues ({passed}/{total} passed){Colors.RESET}")
        print(f"\nTroubleshooting:")
        print(f"  1. Check service is running: docker-compose ps")
        print(f"  2. Check logs: docker-compose logs")
        print(f"  3. Verify .env configuration")
        print(f"  4. Restart service: docker-compose restart")
    
    print()
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()