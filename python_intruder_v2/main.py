import os
import sys
import requests
import urllib3
import multiprocessing
from multiprocessing import Pool

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def read_file(filename):
    """Reads a wordlist from a given file and returns it as a list."""
    try:
        with open(filename, "r") as file:
            wordlist = file.read().splitlines() 
        return wordlist
    except FileNotFoundError:
        print(f"Error: The file {filename} was not found.")
        sys.exit(1)

def send_request(tempConfig, id,fuzz1,fuzz2):
    """Handles sending the request to the target server."""
    tempConfig = tempConfig.splitlines()
    requestType = ""
    path = ""
    headers = {}
    URL = ""
    data = ""
    proxies = {
        'http': 'http://127.0.0.1:8080',
        'https': 'http://127.0.0.1:8080',
    }

    if tempConfig[0].split(" ")[0] == "GET":
        requestType = "GET"
    else:
        requestType = "POST"

    path = tempConfig[0].split(" ")[1]
    URL = "https://" + tempConfig[1].split(": ")[1] + path

    isEmptyLinePassed = False
    for line in tempConfig[2:]:
        if line == "":
            isEmptyLinePassed = True
            continue
        if not isEmptyLinePassed:
            if ": " in line:
                key, value = line.split(": ", 1)
                headers[key] = value
        if isEmptyLinePassed and line:
            data = line

    if requestType == "GET":
        response = requests.get(url=URL, headers=headers, proxies=proxies, verify=False, allow_redirects=False)
    elif requestType == "POST":
        response = requests.post(url=URL, data=data, headers=headers, proxies=proxies, verify=False, allow_redirects=False)
    return (id, response,fuzz1,fuzz2)

def replace_content_and_send(wordlist1, wordlist2, config):
    """Generates configurations with the wordlist replacements and sends them in parallel."""
    tempConfig = config
    jobs = []
    pool_size = 4  # Define the number of parallel processes

    # Creating a pool of workers
    with Pool(pool_size) as pool:
        i = 0
        for fuzz1 in wordlist1:
            for fuzz2 in wordlist2:
                # Replace placeholders with actual values
                modifiedConfig = tempConfig.replace("testUsername", fuzz1).replace("testPassword", fuzz2)
                # Adding task to pool
                jobs.append(pool.apply_async(send_request, (modifiedConfig, str(i),fuzz1,fuzz2)))
                i += 1

        # Collecting results from pool
        results = [job.get() for job in jobs]

    # Update the global dictionary with results
    for result in results:
        id, response,fuzz1,fuzz2 = result
        my_dict[id] = {'response': response, 'fuzz1': fuzz1, 'fuzz2': fuzz2}
def outputDict():
    """Writes the dictionary contents to output.txt with detailed response information including fuzz1 and fuzz2."""
    with open("output.txt", "w") as output_file:
        for key, value in my_dict.items():
            response = value['response']
            fuzz1 = value['fuzz1']
            fuzz2 = value['fuzz2']
            
            # Writing the ID of the request
            output_file.write(f"ID: {key}\n")
            
            # Writing fuzz1 and fuzz2
            output_file.write(f"Fuzz1: {fuzz1}\n")
            output_file.write(f"Fuzz2: {fuzz2}\n")
            
            # Writing HTTP Status Code
            output_file.write(f"Status Code: {response.status_code}\n")
            
            # Writing the full URL of the request
            output_file.write(f"Request URL: {response.url}\n")
            
            # Writing the Response Headers
            #output_file.write(f"Response Headers: {response.headers}\n")
            
            # Writing the Response Body (Text content)
            output_file.write(f"Response Body: {response.text}\n")
            
            # Writing the Response Cookies (if any)
            #output_file.write(f"Response Cookies: {response.cookies}\n")
            
            # Writing the elapsed time for the request
            #output_file.write(f"Request Elapsed Time: {response.elapsed}\n")
            
            # Separator for readability
            output_file.write("-" * 50 + "\n")

    print("Detailed results have been written to output.txt.")



def main():
    """Main function to control the script flow."""
    default_wordlist1 = "wordlist1.txt"
    default_wordlist2 = "wordlist2.txt"
    default_config = "config.txt"

    # Check if default wordlists exist; if not, use command line arguments
    if not (os.path.exists(default_wordlist1) and os.path.exists(default_wordlist2) and os.path.exists(default_config)):
        print("Warning: wordlist1.txt or wordlist2.txt not found in the current directory.")
        if len(sys.argv) != 3:
            print("Alternative Usage: python script.py <wordlist1.txt> <wordlist2.txt> <config.txt>")
            sys.exit(1)
        default_wordlist1 = sys.argv[1]
        default_wordlist2 = sys.argv[2]
        default_config = sys.argv[3]

    wordlist1 = read_file(default_wordlist1) 
    wordlist2 = read_file(default_wordlist2) 
    config = read_file(default_config)

    fullString = ""
    for line in config:
        fullString = fullString + line + "\n"
    config = fullString

    # Call the function to replace content and send requests
    replace_content_and_send(wordlist1, wordlist2, config)

    # Output results
    outputDict()
    for key in my_dict.keys():
        print(key, my_dict[key])  # Print key-value pairs

if __name__ == "__main__":
    my_dict = {}
    main()
