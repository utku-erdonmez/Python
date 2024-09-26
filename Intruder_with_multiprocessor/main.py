import requests
import sys
import os
import multiprocessing

def get_wordlist_from_file(filename):
    """
    Reads a wordlist from the provided file.
    Each word should be on a new line in the file.
    """
    try:
        with open(filename, "r") as file:
            wordlist = file.read().splitlines()  # Read lines and strip newline characters
        return wordlist
    except FileNotFoundError:
        print(f"Error: The file {filename} was not found.")
        sys.exit(1)

def parse_config_file(config_filename):
    """
    Parses the configuration file to extract headers, data, and _URL.
    The first line is ignored, headers are extracted from the lines before
    the blank line, and data and _URL are extracted after the blank line.
    """
    headers = {}
    data = None
    _URL = None
    
    try:
        with open(config_filename, "r") as file:
            lines = file.read().splitlines()  # Read all lines and strip newline characters
            _URL = lines[1].split(": ")[1]
            
            # Ignore the first line
            lines = lines[2:]
            # Separate header lines from data and _URL
            header_part = True
            for line in lines:
                if line == "":
                    header_part = False  # End of headers, start of data
                    continue
                
                if header_part:
                    # Split by ": " to create header key-value pairs
                    if ": " in line:
                        key, value = line.split(": ", 1)
                        headers[key] = value
                else:
                    data = line

    except FileNotFoundError:
        print(f"Error: The file {config_filename} was not found.")
        sys.exit(1)
    
    return headers, data, _URL

import requests
import sys

def send_request(fuzz1, fuzz2, data, headers, proxies, _URL):
    """
    Send a single POST request with the given fuzzing parameters.
    """
    tempData = data.replace("testUsername", fuzz1).replace("testPassword", fuzz2)
    
    try:
        response = requests.post(url=_URL, data=tempData, headers=headers, proxies=proxies, verify=False)
        print(f"Posted data: {tempData}, Status code: {response.status_code}, Response length: {len(response.content)}")
        
        # Open a file and write the status code and response length to it
        with open("output.txt", "a") as file:
            file.write(f"{fuzz1} {fuzz2} Status code: {response.status_code}, Response length: {len(response.content)}\n")
    
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")

def worker(args):
    """
    Worker function to be executed by each process.
    """
    fuzz1, fuzz2, data, headers, proxies, _URL = args
    send_request(fuzz1, fuzz2, data, headers, proxies, _URL)

def send_request_with_fuzzing(wordlist1, wordlist2, data, headers, proxies, _URL):
    """
    Iterate over wordlist1 and wordlist2, replace the placeholder in data, 
    and send POST requests using multiprocessing for better performance.
    """
    # Create a pool of workers
    pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())
    
    tasks = [(fuzz1, fuzz2, data, headers, proxies, _URL) for fuzz1 in wordlist1 for fuzz2 in wordlist2]

    # Distribute tasks across the pool
    pool.map(worker, tasks)
    
    # Close the pool and wait for all workers to finish
    pool.close()
    pool.join()

def main():
    """
    Main function to get wordlists from the current directory if they exist,
    setup request parameters from a config file, and initiate fuzzing.
    """
    # Define default filenames for wordlists
    default_wordlist1 = "wordlist1.txt"
    default_wordlist2 = "wordlist2.txt"

    # Check if wordlists exist in the current directory
    if not (os.path.exists(default_wordlist1) and os.path.exists(default_wordlist2)):
        print("Warning: wordlist1.txt or wordlist2.txt not found in the current directory.")
        if len(sys.argv) != 3:
            print("Alternative Usage: python script.py <wordlist1.txt> <wordlist2.txt>")
            sys.exit(1)
        # Get filenames from command-line arguments
        default_wordlist1 = sys.argv[1]
        default_wordlist2 = sys.argv[2]
        
    # Read wordlists from the provided files
    wordlist1 = get_wordlist_from_file(default_wordlist1)
    wordlist2 = get_wordlist_from_file(default_wordlist2)

    # Parse headers, data, and _URL from the config file
    config_file = "config.txt"
    headers, data, _URL = parse_config_file(config_file)
    _URL = "https://" + _URL
    if not headers or not data or not _URL:
        print("Error: Invalid config file format. Ensure headers, data, and URL are properly defined.")
        sys.exit(1)
    else:
        print(headers, data, _URL)

    # Proxy settings (HTTP and HTTPS)
    proxies = {
        'http': 'http://127.0.0.1:8080',
        'https': 'http://127.0.0.1:8080',
    }
    
    # Start sending requests with fuzzing combinations using multiprocessing
    send_request_with_fuzzing(wordlist1, wordlist2, data, headers, proxies, _URL)

if __name__ == "__main__":
    main()
