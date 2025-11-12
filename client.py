#!/usr/bin/env python3
"""
Simple client for Tardis Download Service.

Usage:
    python client.py --exchange binance --symbols BTC-USDT ETH-USDT \\
                     --start-date 2024-01-01 --end-date 2024-01-02

    python client.py --job-id 123  # Check job status
    python client.py --list-jobs   # List all jobs
"""

import argparse
import sys
import os
import requests
from typing import Optional


class DownloadClient:
    """Client for interacting with the download service."""
    
    def __init__(self, base_url: str = "http://localhost:8000", api_token: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.username = os.getenv('USER', 'unknown')
        self.headers = {
            'X-Username': self.username
        }
        if api_token:
            self.headers['X-API-Token'] = api_token
    
    def submit_download(
        self,
        exchange: str,
        symbols: list,
        start_date: str,
        end_date: str,
        data_types: list = None,
        output_path: str = None
    ):
        """Submit a new download job."""
        if data_types is None:
            data_types = ["trades"]
        
        payload = {
            "exchange": exchange,
            "symbols": symbols,
            "start_date": start_date,
            "end_date": end_date,
            "data_types": data_types
        }
        
        if output_path:
            payload["output_path"] = output_path
        
        try:
            response = requests.post(
                f"{self.base_url}/download",
                json=payload,
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            
            print(f"\n✅ {result['message']}")
            print(f"📊 Job ID: {result['job_id']}")
            print(f"📱 You'll receive Telegram notifications about the progress.")
            print(f"\nCheck status with: python client.py --job-id {result['job_id']}")
            
            return result
            
        except requests.exceptions.HTTPError as e:
            print(f"\n❌ Error: {e}")
            if e.response.text:
                print(f"Details: {e.response.text}")
            sys.exit(1)
        except Exception as e:
            print(f"\n❌ Error: {e}")
            sys.exit(1)
    
    def get_job_status(self, job_id: int):
        """Get the status of a specific job."""
        try:
            response = requests.get(
                f"{self.base_url}/jobs/{job_id}",
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            job = response.json()
            
            status_emoji = {
                "pending": "⏳",
                "running": "🔄",
                "completed": "✅",
                "failed": "❌",
                "cancelled": "🚫"
            }
            
            print(f"\n{status_emoji.get(job['status'], '📊')} Job {job['id']} - {job['status'].upper()}")
            print(f"Exchange: {job['exchange']}")
            print(f"Symbols: {', '.join(job['symbols'])}")
            print(f"Date Range: {job['start_date']} to {job['end_date']}")
            print(f"Created: {job['created_at']}")
            print(f"Created by: {job['created_by']}")
            
            if job['started_at']:
                print(f"Started: {job['started_at']}")
            if job['completed_at']:
                print(f"Completed: {job['completed_at']}")
            if job['error_message']:
                print(f"Error: {job['error_message']}")
            
            return job
            
        except requests.exceptions.HTTPError as e:
            print(f"\n❌ Error: {e}")
            if e.response.text:
                print(f"Details: {e.response.text}")
            sys.exit(1)
        except Exception as e:
            print(f"\n❌ Error: {e}")
            sys.exit(1)
    
    def list_jobs(self, limit: int = 20):
        """List recent jobs."""
        try:
            response = requests.get(
                f"{self.base_url}/jobs",
                params={"limit": limit},
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            
            jobs = result['jobs']
            if not jobs:
                print("\nNo jobs found.")
                return
            
            print(f"\n📋 Recent Jobs (showing {len(jobs)} of {result['total']})")
            print("-" * 80)
            
            for job in jobs:
                status_emoji = {
                    "pending": "⏳",
                    "running": "🔄",
                    "completed": "✅",
                    "failed": "❌",
                    "cancelled": "🚫"
                }
                symbols_str = ', '.join(job['symbols'][:2])
                if len(job['symbols']) > 2:
                    symbols_str += f" (+{len(job['symbols'])-2} more)"
                
                print(f"{status_emoji.get(job['status'], '📊')} Job {job['id']} | "
                      f"{job['status']} | {job['exchange']} | {symbols_str} | "
                      f"by {job['created_by']}")
            
            print("-" * 80)
            
            return jobs
            
        except requests.exceptions.HTTPError as e:
            print(f"\n❌ Error: {e}")
            if e.response.text:
                print(f"Details: {e.response.text}")
            sys.exit(1)
        except Exception as e:
            print(f"\n❌ Error: {e}")
            sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Client for Tardis Download Service",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Submit a download job
  %(prog)s --exchange binance --symbols BTC-USDT ETH-USDT \\
           --start-date 2024-01-01 --end-date 2024-01-02

  # Check job status
  %(prog)s --job-id 123

  # List recent jobs
  %(prog)s --list-jobs
        """
    )
    
    # Server configuration
    parser.add_argument(
        "--url",
        type=str,
        default="http://localhost:8000",
        help="API base URL (default: http://localhost:8000)"
    )
    parser.add_argument(
        "--api-token",
        type=str,
        default=None,
        help="API token for authentication (if required)"
    )
    
    # Job submission arguments
    parser.add_argument("--exchange", type=str, help="Exchange name (e.g., binance)")
    parser.add_argument("--symbols", nargs='+', help="Trading symbols (e.g., BTC-USDT ETH-USDT)")
    parser.add_argument("--start-date", type=str, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end-date", type=str, help="End date (YYYY-MM-DD)")
    parser.add_argument(
        "--data-types",
        nargs='+',
        default=["trades"],
        help="Data types to download (default: trades)"
    )
    parser.add_argument("--output-path", type=str, help="Custom output path")
    
    # Job query arguments
    parser.add_argument("--job-id", type=int, help="Get status of specific job ID")
    parser.add_argument("--list-jobs", action="store_true", help="List recent jobs")
    parser.add_argument("--limit", type=int, default=20, help="Number of jobs to list (default: 20)")
    
    args = parser.parse_args()
    
    # Initialize client
    client = DownloadClient(base_url=args.url, api_token=args.api_token)
    
    # Determine action
    if args.job_id:
        client.get_job_status(args.job_id)
    elif args.list_jobs:
        client.list_jobs(limit=args.limit)
    elif args.exchange and args.symbols and args.start_date and args.end_date:
        client.submit_download(
            exchange=args.exchange,
            symbols=args.symbols,
            start_date=args.start_date,
            end_date=args.end_date,
            data_types=args.data_types,
            output_path=args.output_path
        )
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()