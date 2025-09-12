import socket
import threading
import getpass
import time

# Use '0.0.0.0' to allow connections from other computers on the network.
# Use '127.0.0.1' for local testing only.
HOST = "0.0.0.0"
PORT = 65432
MAX_WRONG_GUESSES = 6

# --- Hangman Art ---
HANGMAN_PICS = [
r'''
  +---+
  |   |
      |
      |
      |
      |
=========''', r'''
  +---+
  |   |
  O   |
      |
      |
      |
=========''', r'''
  +---+
  |   |
  O   |
  |   |
      |
      |
=========''', r'''
  +---+
  |   |
  O   |
 /|   |
      |
      |
=========''', r'''
  +---+
  |   |
  O   |
 /|\  |
      |
      |
=========''', r'''
  +---+
  |   |
  O   |
 /|\  |
 /    |
      |
=========''', r'''
  +---+
  |   |
  O   |
 /|\  |
 / \  |
      |
========='''
]

# --- Game State (Shared) ---
secret_word = ""
guessed_letters = set()
game_over = False

# --- Threading & Connections ---
clients = []
client_threads = []
game_lock = threading.Lock()

def reset_game_state():
    """Resets all variables for a new game."""
    global secret_word, guessed_letters, game_over, clients, client_threads
    secret_word = ""
    guessed_letters = set()
    game_over = False
    for c in clients:
        c.close()
    clients = []
    client_threads = []

def get_game_state():
    """Constructs the current game state string including hangman art."""
    wrong_guesses = sorted(list(guessed_letters - set(secret_word)))
    wrong_guesses_count = len(wrong_guesses)
    
    art = HANGMAN_PICS[wrong_guesses_count]
    
    masked_word = ""
    for letter in secret_word:
        if letter in guessed_letters:
            masked_word += letter + " "
        else:
            masked_word += "_ "
    
    return f"{art}\n\nWord: {masked_word}\nWrong guesses ({wrong_guesses_count}/{MAX_WRONG_GUESSES}): {' '.join(wrong_guesses)}\n"

def broadcast(message):
    """Sends a message to all connected clients."""
    for client_conn in clients:
        try:
            client_conn.sendall(message.encode('utf-8'))
        except socket.error:
            pass

def handle_client(conn, addr):
    """Handles a single client connection in a separate thread."""
    global game_over
    print(f"Connected by {addr}")
    
    with game_lock:
        clients.append(conn)

    try:
        initial_state = get_game_state()
        conn.sendall(initial_state.encode('utf-8'))

        while not game_over:
            try:
                data = conn.recv(1024)
                if not data:
                    break

                guess = data.decode('utf-8').strip().lower()
                if not guess or len(guess) > 1:
                    continue
                
                with game_lock:
                    if game_over:
                        break

                    if guess not in guessed_letters:
                        guessed_letters.add(guess)
                        
                        if set(secret_word).issubset(guessed_letters):
                            final_state = get_game_state()
                            message = f"\n{final_state}\n*** Player {addr} won! The word was '{secret_word}'. ***"
                            game_over = True
                        else:
                            wrong_guesses_count = len(guessed_letters - set(secret_word))
                            if wrong_guesses_count >= MAX_WRONG_GUESSES:
                                final_state = get_game_state()
                                message = f"\n{final_state}\n*** Game Over! You lost. The word was '{secret_word}'. ***"
                                game_over = True
                            else:
                                message = f"Player {addr} guessed '{guess}'.\n" + get_game_state()
                        
                        broadcast(message)

            except (socket.error, UnicodeDecodeError):
                break
    finally:
        print(f"Connection from {addr} closed.")
        with game_lock:
            if conn in clients:
                clients.remove(conn)
        conn.close()

def main():
    """Main function to start the server and manage game loops."""
    global secret_word, game_over, client_threads

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # This allows the server to reuse the same address, avoiding "Address already in use" errors
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen()
    print(f"Hangman server started on {HOST}:{PORT}")

    while True:
        reset_game_state()

        while not secret_word:
            try:
                word_input = getpass.getpass("Enter the secret word for the new game: ").strip().lower()
                if " " in word_input or not word_input:
                    print("Word cannot contain spaces or be empty. Please try again.")
                else:
                    secret_word = word_input
            except (KeyboardInterrupt, EOFError):
                print("\nShutting down server.")
                server_socket.close()
                return

        print("New game started. Ready for players.")
        server_socket.settimeout(1.0)

        while not game_over:
            try:
                conn, addr = server_socket.accept()
                thread = threading.Thread(target=handle_client, args=(conn, addr))
                thread.daemon = True
                thread.start()
                client_threads.append(thread)
            except socket.timeout:
                continue
            except KeyboardInterrupt:
                game_over = True
        
        print("Game over. Cleaning up...")
        for thread in client_threads:
            thread.join(timeout=2.0)
        
        broadcast("Server is restarting for a new game...")
        time.sleep(1)
        for c in clients:
            c.close()

        while True:
            try:
                play_again = input("Play another game? (y/n): ").strip().lower()
                if play_again in ['y', 'n']:
                    break
            except (KeyboardInterrupt, EOFError):
                play_again = 'n'
                break
        
        if play_again == 'n':
            print("Shutting down server.")
            break

    server_socket.close()

if __name__ == "__main__":
    main()
