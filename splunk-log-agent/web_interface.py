#!/usr/bin/env python3
"""
Web interface for the Splunk Log Reader Agent
"""

import json
from flask import Flask, render_template, request, jsonify
from splunk_log_reader import load_config, connect_to_splunk, run_search, format_time_range

app = Flask(__name__)
service = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/search', methods=['POST'])
def search():
    data = request.json
    query = data.get('query', '')
    earliest = data.get('earliest', '')
    latest = data.get('latest', '')
    max_results = int(data.get('max_results', 100))
    
    earliest_time = format_time_range(earliest) if earliest else None
    latest_time = format_time_range(latest) if latest else None
    
    events = run_search(service, query, earliest_time, latest_time, max_results)
    return jsonify(events)

def create_templates():
    """Create the HTML templates for the web interface"""
    import os
    
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    
    # Create index.html template
    with open('templates/index.html', 'w') as f:
        f.write('''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Splunk Log Reader</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            margin-top: 0;
        }
        .form-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        input[type="text"], input[type="number"], textarea {
            width: 100%;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
            box-sizing: border-box;
        }
        textarea {
            height: 100px;
            font-family: monospace;
        }
        button {
            background-color: #4CAF50;
            color: white;
            padding: 10px 15px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        button:hover {
            background-color: #45a049;
        }
        .results {
            margin-top: 20px;
            border-top: 1px solid #ddd;
            padding-top: 20px;
        }
        .event {
            background-color: #f9f9f9;
            padding: 10px;
            margin-bottom: 10px;
            border-radius: 4px;
            border-left: 3px solid #4CAF50;
        }
        .loading {
            text-align: center;
            padding: 20px;
            display: none;
        }
        .field {
            margin-bottom: 5px;
        }
        .field-name {
            font-weight: bold;
            color: #555;
        }
        .field-value {
            font-family: monospace;
            word-break: break-all;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Splunk Log Reader</h1>
        
        <div class="form-group">
            <label for="query">Search Query:</label>
            <textarea id="query" placeholder="Enter your Splunk search query, e.g., 'search index=main error'"></textarea>
        </div>
        
        <div class="form-group">
            <label for="earliest">Earliest Time:</label>
            <input type="text" id="earliest" placeholder="e.g., 24h, 7d, YYYY-MM-DD">
        </div>
        
        <div class="form-group">
            <label for="latest">Latest Time (optional):</label>
            <input type="text" id="latest" placeholder="e.g., now, YYYY-MM-DD">
        </div>
        
        <div class="form-group">
            <label for="max-results">Max Results:</label>
            <input type="number" id="max-results" value="100" min="1" max="1000">
        </div>
        
        <button id="search-btn">Search</button>
        
        <div class="loading" id="loading">
            <p>Searching Splunk logs...</p>
        </div>
        
        <div class="results" id="results">
            <h2>Results</h2>
            <div id="events-container"></div>
        </div>
    </div>
    
    <script>
        document.getElementById('search-btn').addEventListener('click', function() {
            const query = document.getElementById('query').value.trim();
            if (!query) {
                alert('Please enter a search query');
                return;
            }
            
            const earliest = document.getElementById('earliest').value.trim();
            const latest = document.getElementById('latest').value.trim();
            const maxResults = document.getElementById('max-results').value;
            
            // Show loading indicator
            document.getElementById('loading').style.display = 'block';
            document.getElementById('events-container').innerHTML = '';
            
            // Send search request
            fetch('/api/search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    query: query,
                    earliest: earliest,
                    latest: latest,
                    max_results: maxResults
                })
            })
            .then(response => response.json())
            .then(data => {
                // Hide loading indicator
                document.getElementById('loading').style.display = 'none';
                
                // Display results
                const eventsContainer = document.getElementById('events-container');
                
                if (data.length === 0) {
                    eventsContainer.innerHTML = '<p>No results found.</p>';
                    return;
                }
                
                data.forEach((event, index) => {
                    const eventDiv = document.createElement('div');
                    eventDiv.className = 'event';
                    
                    const eventTitle = document.createElement('h3');
                    eventTitle.textContent = `Event ${index + 1}`;
                    eventDiv.appendChild(eventTitle);
                    
                    for (const [key, value] of Object.entries(event)) {
                        const fieldDiv = document.createElement('div');
                        fieldDiv.className = 'field';
                        
                        const fieldName = document.createElement('div');
                        fieldName.className = 'field-name';
                        fieldName.textContent = key;
                        
                        const fieldValue = document.createElement('div');
                        fieldValue.className = 'field-value';
                        fieldValue.textContent = typeof value === 'object' ? JSON.stringify(value) : value;
                        
                        fieldDiv.appendChild(fieldName);
                        fieldDiv.appendChild(fieldValue);
                        eventDiv.appendChild(fieldDiv);
                    }
                    
                    eventsContainer.appendChild(eventDiv);
                });
            })
            .catch(error => {
                document.getElementById('loading').style.display = 'none';
                alert('Error: ' + error.message);
                console.error('Error:', error);
            });
        });
    </script>
</body>
</html>''')

def main():
    global service
    
    # Create HTML templates
    create_templates()
    
    # Load configuration
    config = load_config()
    
    # Connect to Splunk
    service = connect_to_splunk(config)
    print(f"Connected to Splunk at {config['host']}:{config['port']}")
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=12000, debug=True)

if __name__ == "__main__":
    main()