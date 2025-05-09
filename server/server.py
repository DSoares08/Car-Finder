import http.server
import socketserver
import threading
import time
import sys
import os
import json
from datetime import datetime
import importlib.util
import traceback

# Add the parent directory to the path so we can import the main script
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Store found cars
found_cars = []
last_run_time = None
last_run_status = "Not run yet"
is_running = False
run_lock = threading.Lock()

def load_main_script():
    """Load the main.py script as a module without executing it directly"""
    spec = importlib.util.spec_from_file_location(
        "car_finder", 
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "main.py")
    )
    car_finder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(car_finder)
    return car_finder

def run_automation():
    """Run the automation script and capture the results"""
    global last_run_time, last_run_status, is_running, found_cars
    
    with run_lock:
        if is_running:
            return "Automation already running"
        is_running = True
    
    last_run_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    last_run_status = "Running..."
    
    try:
        # Create a custom stdout to capture print statements
        import io
        from contextlib import redirect_stdout
        
        output = io.StringIO()
        
        with redirect_stdout(output):
            # Import and run the main script in a controlled environment
            car_finder = load_main_script()
            
            # Call the run_search function
            result_link = car_finder.run_search()
            
            # Access the found cars after execution
            if hasattr(car_finder, 'found_cars') and car_finder.found_cars:
                for car_url in car_finder.found_cars:
                    # Add to found cars if not already there
                    if car_url not in [car['url'] for car in found_cars]:
                        found_cars.append({
                            'url': car_url,
                            'found_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        })
        
        # Get the output
        output_text = output.getvalue()
        last_run_status = "Success" if "Found car at URL" in output_text else "Completed with no cars found"
        
        # Extract any URLs from the output
        import re
        urls = re.findall(r'Found car at URL: (https?://[^\s]+)', output_text)
        for url in urls:
            if url not in [car['url'] for car in found_cars]:
                found_cars.append({
                    'url': url,
                    'found_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
        
        return output_text
    
    except Exception as e:
        error_trace = traceback.format_exc()
        last_run_status = f"Error: {str(e)}"
        return f"Error running automation: {str(e)}\n{error_trace}"
    
    finally:
        with run_lock:
            is_running = False

class AutomationHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            # Create a simple HTML page
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Car Finder Automation</title>
                <meta http-equiv="refresh" content="10">
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    h1 {{ color: #333; }}
                    .status {{ padding: 10px; background-color: #f0f0f0; border-radius: 5px; }}
                    .car-list {{ margin-top: 20px; }}
                    .car-item {{ padding: 10px; margin-bottom: 5px; background-color: #e9f7fe; border-radius: 5px; }}
                    .controls {{ margin: 20px 0; }}
                    button {{ padding: 10px; background-color: #4CAF50; color: white; border: none; cursor: pointer; }}
                </style>
            </head>
            <body>
                <h1>Car Finder Automation</h1>
                
                <div class="status">
                    <p><strong>Last Run:</strong> {last_run_time or 'Never'}</p>
                    <p><strong>Status:</strong> {last_run_status}</p>
                    <p><strong>Currently Running:</strong> {'Yes' if is_running else 'No'}</p>
                </div>
                
                <div class="controls">
                    <a href="/run"><button>Run Now</button></a>
                </div>
                
                <h2>Found Cars ({len(found_cars)})</h2>
                <div class="car-list">
            """
            
            if not found_cars:
                html += "<p>No cars found yet.</p>"
            else:
                for i, car in enumerate(found_cars):
                    html += f"""
                    <div class="car-item">
                        <p><strong>Car #{i+1}</strong></p>
                        <p><strong>URL:</strong> <a href="{car['url']}" target="_blank">{car['url']}</a></p>
                        <p><strong>Found At:</strong> {car['found_at']}</p>
                    </div>
                    """
            
            html += """
                </div>
            </body>
            </html>
            """
            
            self.wfile.write(html.encode())
            
        elif self.path == '/run':
            # Trigger a manual run
            threading.Thread(target=self.run_and_redirect).start()
            
            self.send_response(302)
            self.send_header('Location', '/')
            self.end_headers()
            
        elif self.path == '/api/status':
            # Return status as JSON
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            status = {
                'last_run': last_run_time,
                'status': last_run_status,
                'is_running': is_running,
                'found_cars': found_cars
            }
            
            self.wfile.write(json.dumps(status).encode())
            
        else:
            self.send_error(404)
    
    def run_and_redirect(self):
        """Run the automation and then redirect"""
        run_automation()

def scheduled_run():
    """Function to run the automation on a schedule"""
    while True:
        try:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Running scheduled automation...")
            result = run_automation()
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Completed with status: {last_run_status}")
        except Exception as e:
            print(f"Error in scheduled run: {str(e)}")
        
        # Wait for the next run
        time.sleep(20)  # Run every 20 seconds

def start_server(port=8000):
    """Start the HTTP server"""
    handler = AutomationHandler
    
    # Start the scheduler in a separate thread
    scheduler = threading.Thread(target=scheduled_run, daemon=True)
    scheduler.start()
    
    # Start the HTTP server
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"Server started at http://localhost:{port}")
        httpd.serve_forever()

if __name__ == "__main__":
    port = 8000
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"Invalid port number: {sys.argv[1]}")
            sys.exit(1)
    
    start_server(port)
