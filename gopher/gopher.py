import socket
import re  

host = 'gopher.black'
port = 70

def send_request(input=""):


    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
 
        s.connect((host, port))

        initial_data=input+"\r\n"
        s.sendall(bytes(initial_data.encode("utf-8")))

        response = b""
        while True:
            data = s.recv(4096)
            if not data:
                break
            response += data


    response_decoded = response.decode('utf-8', errors='ignore')
    if ".txt" in input:
        print(response_decoded)
        return response_decoded
   
    lines = response_decoded.splitlines()
   
    formatted_words = []
    for line in lines:
        line=line.split("\t")
        
        if line[0].startswith('i'):
            

            formatted_word = line[0][1:]  
        elif line[0].startswith('1'):
          
            formatted_word = f"[ DIR ] {line[0][1:]+"\t"+line[1]}"
        elif line[0].startswith("0"):
            
            formatted_word = "[ FILE ] "+line[0][1:]+"\t"+line[1]
        elif line[0].startswith("h"):
        
            formatted_word = "[ HTML ] "+line[0][1:]+"\t"+line[1]



        else:
            formatted_word = line

        formatted_words.append(formatted_word)

    for word in formatted_words:
        print(word)
    return formatted_words
def main():
    send_request()
    while True:
        input_path=input("> (add '/' if needed, send empty input for root directory ): ")
        send_request(input_path)

if "__main__":
    main()


