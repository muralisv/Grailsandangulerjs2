#!/usr/bin/env python3
"""
Splunk Log Reader Agent

A simple agent that connects to Splunk and reads logs based on search queries.
"""

import os
import sys
import time
from datetime import datetime, timedelta
import argparse
from dotenv import load_dotenv

try:
    import splunklib.client as client
    import splunklib.results as results
except ImportError:
    print("Error: splunk-sdk package not installed.")
    print("Please install required packages using: pip install -r requirements.txt")
    sys.exit(1)

def load_config():
    """Load configuration from .env file"""
    load_dotenv()
    
    config = {
        'host': os.getenv('SPLUNK_HOST'),
        'port': os.getenv('SPLUNK_PORT', 8089),
        'username': os.getenv('SPLUNK_USERNAME'),
        'password': os.getenv('SPLUNK_PASSWORD'),
        'scheme': os.getenv('SPLUNK_SCHEME', 'https')
    }
    
    # Check if required config values are present
    missing = [k for k, v in config.items() if v is None]
    if missing:
        print(f"Error: Missing required configuration: {', '.join(missing)}")
        print("Please create a .env file based on .env.example")
        sys.exit(1)
        
    return config

def connect_to_splunk(config):
    """Connect to Splunk using the provided configuration"""
    try:
        service = client.connect(
            host=config['host'],
            port=config['port'],
            username=config['username'],
            password=config['password'],
            scheme=config['scheme']
        )
        return service
    except Exception as e:
        print(f"Error connecting to Splunk: {e}")
        sys.exit(1)

def run_search(service, search_query, earliest_time=None, latest_time=None, max_results=100):
    """Run a search query on Splunk and return the results"""
    kwargs = {
        "earliest_time": earliest_time,
        "latest_time": latest_time,
        "exec_mode": "normal",
        "count": max_results
    }
    
    # Remove None values
    kwargs = {k: v for k, v in kwargs.items() if v is not None}
    
    try:
        # Run the search
        job = service.jobs.create(search_query, **kwargs)
        
        # Wait for the job to complete
        while not job.is_done():
            time.sleep(0.5)
        
        # Get the results
        result_count = int(job["resultCount"])
        if result_count == 0:
            print("No results found.")
            return []
        
        # Print the results
        result_stream = job.results(output_mode="json")
        reader = results.JSONResultsReader(result_stream)
        
        events = []
        for result in reader:
            if isinstance(result, dict):
                events.append(result)
        
        return events
    except Exception as e:
        print(f"Error running search: {e}")
        return []

def format_time_range(time_range):
    """Convert a time range string to Splunk format"""
    if not time_range:
        return None
    
    now = datetime.now()
    
    if time_range == "today":
        return now.strftime("%Y-%m-%d:00:00:00")
    elif time_range == "yesterday":
        yesterday = now - timedelta(days=1)
        return yesterday.strftime("%Y-%m-%d:00:00:00")
    elif time_range.endswith("h"):
        hours = int(time_range[:-1])
        past_time = now - timedelta(hours=hours)
        return past_time.strftime("%Y-%m-%dT%H:%M:%S")
    elif time_range.endswith("d"):
        days = int(time_range[:-1])
        past_time = now - timedelta(days=days)
        return past_time.strftime("%Y-%m-%dT%H:%M:%S")
    elif time_range.endswith("m"):
        minutes = int(time_range[:-1])
        past_time = now - timedelta(minutes=minutes)
        return past_time.strftime("%Y-%m-%dT%H:%M:%S")
    else:
        return time_range

def display_results(events, output_format="text"):
    """Display the search results in the specified format"""
    if not events:
        return
    
    if output_format == "text":
        for i, event in enumerate(events, 1):
            print(f"\n--- Event {i} ---")
            for key, value in event.items():
                print(f"{key}: {value}")
    elif output_format == "json":
        import json
        print(json.dumps(events, indent=2))
    else:
        print("Unsupported output format")

def main():
    parser = argparse.ArgumentParser(description="Splunk Log Reader Agent")
    parser.add_argument("query", nargs="?", help="Splunk search query")
    parser.add_argument("--earliest", "-e", help="Earliest time for the search (e.g., '24h', '7d', 'YYYY-MM-DD')")
    parser.add_argument("--latest", "-l", help="Latest time for the search")
    parser.add_argument("--max-results", "-m", type=int, default=100, help="Maximum number of results to return")
    parser.add_argument("--format", "-f", choices=["text", "json"], default="text", help="Output format")
    parser.add_argument("--interactive", "-i", action="store_true", help="Run in interactive mode")
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config()
    
    # Connect to Splunk
    service = connect_to_splunk(config)
    print(f"Connected to Splunk at {config['host']}:{config['port']}")
    
    if args.interactive:
        while True:
            query = input("\nEnter search query (or 'exit' to quit): ")
            if query.lower() == 'exit':
                break
                
            earliest = input("Earliest time (e.g., '24h', '7d', or press Enter for all time): ")
            max_results = input("Max results (default 100): ")
            
            earliest_time = format_time_range(earliest) if earliest else None
            max_results = int(max_results) if max_results else 100
            
            print(f"\nRunning query: {query}")
            print(f"Time range: {earliest_time or 'all time'} to now")
            print(f"Max results: {max_results}")
            
            events = run_search(service, query, earliest_time, None, max_results)
            display_results(events, args.format)
    else:
        if not args.query:
            parser.print_help()
            sys.exit(1)
            
        earliest_time = format_time_range(args.earliest)
        latest_time = format_time_range(args.latest)
        
        print(f"Running query: {args.query}")
        print(f"Time range: {earliest_time or 'all time'} to {latest_time or 'now'}")
        print(f"Max results: {args.max_results}")
        
        events = run_search(service, args.query, earliest_time, latest_time, args.max_results)
        display_results(events, args.format)

if __name__ == "__main__":
    main()