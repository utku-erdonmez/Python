import sys

"""
Adjust the filter values as needed.
"""

def get_wordlist_from_file(filename):
    try:
        with open(filename, "r") as file:
            return file.read().splitlines()
    except FileNotFoundError:
        print(f"Error: The file {filename} was not found.")
        sys.exit(1)

# Load data
lines = get_wordlist_from_file("output.txt")

filtered_by_time = []
filtered_by_length = []
filtered_by_code = []

for line in lines:
    try:
        response_time = float(line.split("Response time: ")[1].split(" ")[0])
        response_length = int(line.split("Response length: ")[1].split(",")[0])
        status_code = int(line.split("Status code: ")[1].split(",")[0])

        if response_time > 0.71:
            filtered_by_time.append(line)
        if response_length > 5555:
            filtered_by_length.append(line)
        if status_code != 200:
            filtered_by_code.append(line)

    except (IndexError, ValueError) as e:
        print(f"Error processing line: '{line}'. Skipping. Error: {e}")

# Prepare output
output_content = [
    "Response Time \n" + "\n".join(filtered_by_time),
    "\nResponse Length\n" + "\n".join(filtered_by_length),
    "\nFiltered by status code \n" + "\n".join(filtered_by_code)
]

# Write results
with open("filter_output.txt", "w") as output_file:
    output_file.write("\n\n".join(output_content))

print("Filtered results have been written to output2.txt")
