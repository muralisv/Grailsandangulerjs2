#!/usr/bin/env python3
"""
Example usage of the Splunk Log Reader Agent as a library
"""

from splunk_log_reader import load_config, connect_to_splunk, run_search, display_results

def main():
    # Load configuration from .env file
    config = load_config()
    
    # Connect to Splunk
    service = connect_to_splunk(config)
    print(f"Connected to Splunk at {config['host']}:{config['port']}")
    
    # Define search parameters
    search_query = "search index=main error"
    earliest_time = "-24h"  # Last 24 hours
    max_results = 50
    
    print(f"Running query: {search_query}")
    print(f"Time range: {earliest_time} to now")
    print(f"Max results: {max_results}")
    
    # Run the search
    events = run_search(service, search_query, earliest_time, None, max_results)
    
    # Display the results
    display_results(events, "text")
    
    # Example of another search
    print("\n--- Running another search ---")
    search_query = "search index=application source=*/app.log | head 10"
    events = run_search(service, search_query)
    display_results(events, "text")

if __name__ == "__main__":
    main()