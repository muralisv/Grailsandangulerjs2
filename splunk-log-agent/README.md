# Splunk Log Reader Agent

A simple Python agent that connects to Splunk and reads logs based on search queries.

## Features

- Connect to Splunk using the Splunk SDK
- Run search queries with time range filters
- Display results in text or JSON format
- Interactive mode for running multiple queries
- Command-line interface for scripting

## Installation

1. Clone this repository:
   ```
   git clone <repository-url>
   cd splunk-log-agent
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Create a `.env` file with your Splunk connection details:
   ```
   cp .env.example .env
   ```
   
   Edit the `.env` file with your Splunk credentials:
   ```
   SPLUNK_HOST=your_splunk_host
   SPLUNK_PORT=8089
   SPLUNK_USERNAME=your_username
   SPLUNK_PASSWORD=your_password
   SPLUNK_SCHEME=https
   ```

## Usage

### Command-line Mode

Run a specific search query:

```bash
python splunk_log_reader.py "search index=main error" --earliest 24h --max-results 50
```

Options:
- `--earliest` or `-e`: Earliest time for the search (e.g., '24h', '7d', 'YYYY-MM-DD')
- `--latest` or `-l`: Latest time for the search
- `--max-results` or `-m`: Maximum number of results to return (default: 100)
- `--format` or `-f`: Output format (text or json, default: text)

### Interactive Mode

Run the agent in interactive mode to execute multiple queries:

```bash
python splunk_log_reader.py --interactive
```

In interactive mode, you'll be prompted to:
1. Enter a search query
2. Specify the time range
3. Set the maximum number of results

### Web Interface

The agent also provides a web interface for easier interaction:

```bash
python web_interface.py
```

This will start a web server on port 12000. You can access the web interface by opening a browser and navigating to:
```
http://localhost:12000
```

The web interface provides a user-friendly way to:
- Enter search queries
- Specify time ranges
- View results in a formatted display

### Programmatic Usage

You can also use the agent as a library in your own Python scripts:

```python
from splunk_log_reader import load_config, connect_to_splunk, run_search, display_results

# Load configuration
config = load_config()

# Connect to Splunk
service = connect_to_splunk(config)

# Run a search
events = run_search(service, "search index=main error", "-24h", None, 100)

# Process the results
for event in events:
    # Do something with each event
    print(event)
```

See `example_usage.py` for a complete example.

## Examples

1. Search for error logs from the last 24 hours:
   ```
   python splunk_log_reader.py "search index=main error" --earliest 24h
   ```

2. Search for specific application logs with JSON output:
   ```
   python splunk_log_reader.py "search index=application source=*/app.log" --earliest 7d --format json
   ```

3. Run in interactive mode:
   ```
   python splunk_log_reader.py --interactive
   ```

## License

MIT