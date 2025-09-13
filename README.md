# Multiplayer Hangman Game (TCP)

![Python 3.x](https://img.shields.io/badge/Python-3.x-blue.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Status](https://img.shields.io/badge/status-finished-green)

This project is a multiplayer version of the classic Hangman game, using TCP sockets for communication between a server and multiple clients.

## Project Objective

This project was developed as a practical assignment for the **SIN352 - Computer Networks** course. Its main goal is to apply the concepts of inter-process communication using the Sockets API in a practical way.

Through the implementation of this game, the following topics were explored:

-   Creating and managing **TCP** sockets.
-   Implementing the client-server model.
-   Handling multiple simultaneous connections using **threads**.
-   Exchanging messages to keep an application's state synchronized across different processes on the network.

## Features

-   **Authoritative Server:** The server manages the secret word and the entire game state.
-   **Real-time Multiplayer:** Multiple clients can connect and play the same match simultaneously.
-   **Command-Line Interface:** Simple and direct interaction through the terminal, with ASCII art to represent the hangman.
-   **Play Again Feature:** The server can start new matches without needing to be restarted.

## Prerequisites

-   Python 3.x

## How to Run

The system consists of two scripts: `hangman-server.py` and `hangman-client.py`.

### 1. Start the Server

First, start the server in a terminal.

```bash
python hangman-server.py
```

The server will prompt you to **enter the secret word** for the match. The word will not be displayed on the screen. After entering it, the server will be ready to accept player connections.

### 2. Start the Client(s)

For each player, open a **new terminal** and run the following command:

```bash
python hangman-client.py
```

The client will automatically connect to the server.

### 3. Configuring the Connection

By default, the client (`hangman-client.py`) is configured to connect to a server running on the same machine (`HOST = "127.0.0.1"`).

If the server is running on a different machine on the same local network, you need to:

1.  **Find the local IP address** of the machine where the server is running.
2.  **Open the `hangman-client.py` file** and change the `HOST` variable to the server's IP address.

For example:

```python
# Before
HOST = "127.0.0.1"

# After (if the server's IP is 192.168.1.10)
HOST = "192.168.1.10"
```

## How to Play

1.  As soon as the client connects, the current game state (the hangman art, the masked word, and the wrong letters) is displayed.
2.  In the client's terminal, type a letter and press `Enter` to make your guess.
3.  The game state will be updated for all connected players.
4.  The game ends when a player guesses the word or when the maximum number of errors (6) is reached.
5.  At the end of the match, the server operator will be asked if a new match should be started.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.