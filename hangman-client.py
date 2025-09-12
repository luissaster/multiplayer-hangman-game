import socket
import threading
import os
import sys

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 65432        # The port used by the server

def receive_messages(sock):
    """Continuously receives messages from the server and prints them."""
    while True:
        try:
            data = sock.recv(1024)
            if not data:
                print("\nConnection lost from server.")
                # Use os._exit to force close the client, including the input thread
                os._exit(0)
            
            # Clear the current line and print the new state
            sys.stdout.write("\r" + " " * 60 + "\r") # Clear line
            print(data.decode('utf-8'))
            sys.stdout.write("Enter a letter: ") # Reprint prompt
            sys.stdout.flush()

        except (ConnectionResetError, ConnectionAbortedError):
            print("\nConnection to server has been closed.")
            os._exit(0)
        except Exception as e:
            print(f"An error occurred while receiving data: {e}")
            os._exit(1)

def main():
    """Main function to connect to the server and handle user input."""
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((HOST, PORT))
        print("Connected to the Hangman server! Waiting for game to start...")
    except ConnectionRefusedError:
        print(f"Connection failed. Is the server running on {HOST}:{PORT}?")
        return

    # Start a thread to listen for server messages
    receiver_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    receiver_thread.daemon = True
    receiver_thread.start()

    # Main thread for user input
    while True:
        try:
            guess = input("Enter a letter: ")
            if guess:
                client_socket.sendall(guess.encode('utf-8'))
        except KeyboardInterrupt:
            print("\nDisconnecting...")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            break
    
    client_socket.close()

if __name__ == "__main__":
    main()
