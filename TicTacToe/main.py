import mysql.connector
from datetime import datetime
import tkinter as tk
from tkinter import messagebox
 
# Factory Pattern: Create players dynamically
class PlayerFactory:
    @staticmethod # we don't need to create an object to use this method
    def create_player(name, symbol):
        return {"name": name, "symbol": symbol} # this makes changing players in the future easy

# WinStrategy Interface (Strategy Pattern)
class WinStrategy:
    def check_winner(self, board):
        raise NotImplementedError # this forces anyone who creates a class based on WinStrategy to define how check_winner works.

class StandardWinStrategy(WinStrategy):
    def check_winner(self, board):
        winning_combos = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],
            [0, 3, 6], [1, 4, 7], [2, 5, 8],
            [0, 4, 8], [2, 4, 6]
        ]
        for combo in winning_combos:
            a, b, c = combo
            if board[a] == board[b] == board[c] and board[a] is not None:
                return True
        return False

# Observer Pattern: Notifying the GUI about game state changes
class GameObserver: # abstract
    def update(self, event, data):
        pass

class TicTacToeGame:
    def __init__(self, win_strategy=None):
        self.board = [None] * 9 # Clears The board
        self.current_player = 0
        self.players = [{"name": "Player 1", "symbol": "X"}, {"name": "Player 2", "symbol": "O"}]
        self.observers = []  # List of observers
        self.win_strategy = win_strategy or StandardWinStrategy()

    def add_observer(self, observer):
        self.observers.append(observer)

    def notify_observers(self, event, data):
        for observer in self.observers:
            observer.update(event, data)

    def reset_game(self):
        self.board = [None] * 9
        self.current_player = 0

    def make_move(self, index):
        symbol = self.players[self.current_player]["symbol"]
        self.board[index] = symbol
        self.current_player = 1 - self.current_player
        self.notify_observers("move_made", self.board)

    def check_winner(self):
        return self.win_strategy.check_winner(self.board)

    def is_draw(self):
        return None not in self.board # there is no empty cell

class DatabaseManager:
    def __init__(self, connection):
        self.connection = connection
        self.cursor = self.connection.cursor()

    def create_table(self):
        create_table_query = """
        CREATE TABLE IF NOT EXISTS info (
            id INT AUTO_INCREMENT PRIMARY KEY,
            player1_name VARCHAR(255),
            player1_symbol VARCHAR(10),
            player2_name VARCHAR(255),
            player2_symbol VARCHAR(10),
            result VARCHAR(255),
            timestamp VARCHAR(255)
        )
        """
        self.cursor.execute(create_table_query)
        self.connection.commit()

    def save_game(self, game_data):
        insert_query = """
        INSERT INTO info (player1_name, player1_symbol, player2_name, player2_symbol, result, timestamp)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        self.cursor.execute(insert_query, game_data)
        self.connection.commit()

class TicTacToeGUI(GameObserver):
    def __init__(self, game, db_manager):
        self.window = tk.Tk()
        self.window.title("Tic Tac Toe - GUI Edition")
        self.window.configure(bg="#2c3e50")
        self.game = game
        self.db_manager = db_manager
        self.game.add_observer(self)
        self.create_main_menu()

    def clear_window(self):
        for widget in self.window.winfo_children():
            widget.destroy()

    def create_main_menu(self):
        self.clear_window()
        tk.Label(self.window, text="Welcome to Tic Tac Toe!", font=("Helvetica", 24, "bold"), bg="#2c3e50", fg="#ecf0f1").pack(pady=20)

        tk.Button(self.window, text="Start Game", font=("Helvetica", 16), bg="#27ae60", fg="white", command=self.setup_players,
                  relief="flat", bd=0, highlightthickness=0, activebackground="#2ecc71", activeforeground="white").pack(pady=10)
        tk.Button(self.window, text="Quit", font=("Helvetica", 16), bg="#c0392b", fg="white", command=self.window.quit,
                  relief="flat", bd=0, highlightthickness=0, activebackground="#e74c3c", activeforeground="white").pack(pady=10)

    def setup_players(self):
        self.clear_window()
        self.player_entries = []

        tk.Label(self.window, text="Enter Player Details", font=("Helvetica", 20, "bold"), bg="#2c3e50", fg="#ecf0f1").pack(pady=10)

        for i in range(2):
            tk.Label(self.window, text=f"Player {i + 1} Name:", font=("Helvetica", 14), bg="#2c3e50", fg="#ecf0f1").pack()
            name_entry = tk.Entry(self.window, font=("Helvetica", 14))
            name_entry.pack(pady=5)

            tk.Label(self.window, text=f"Player {i + 1} Symbol (1 letter):", font=("Helvetica", 14), bg="#2c3e50", fg="#ecf0f1").pack()
            symbol_entry = tk.Entry(self.window, font=("Helvetica", 14), width=3)
            symbol_entry.pack(pady=5)

            self.player_entries.append((name_entry, symbol_entry))

        tk.Button(self.window, text="Start", font=("Helvetica", 16), bg="#27ae60", fg="white", command=self.start_game,
                  relief="flat", bd=0, highlightthickness=0, activebackground="#2ecc71", activeforeground="white").pack(pady=20)

    def start_game(self):
        self.game.reset_game()
        used_symbols = set()
        for i, (name_entry, symbol_entry) in enumerate(self.player_entries):
            name = name_entry.get().strip()
            symbol = symbol_entry.get().strip().upper()

            if not name or not symbol or len(symbol) != 1 or not symbol.isalpha():
                messagebox.showerror("Input Error", "Please enter valid names and single-letter symbols.")
                return
            if not name.isalpha():
                messagebox.showerror("Input Error", f"Player {i + 1}'s name must contain only letters.")
                return
            if symbol in used_symbols:
                messagebox.showerror("Input Error", f"Symbol '{symbol}' is already taken. Choose another one.")
                return

            self.game.players[i] = PlayerFactory.create_player(name, symbol)
            used_symbols.add(symbol)

        self.show_board()

    def show_board(self):
        self.clear_window()
        tk.Label(self.window, text=f"{self.game.players[self.game.current_player]['name']}'s Turn ({self.game.players[self.game.current_player]['symbol']})",
                 font=("Helvetica", 18), bg="#2c3e50", fg="#ecf0f1").pack(pady=10)

        board_frame = tk.Frame(self.window, bg="#2c3e50")
        board_frame.pack()

        for i in range(9):
            btn = tk.Button(board_frame, text=self.game.board[i] if self.game.board[i] else "", font=("Helvetica", 20, "bold"),
                            height=2, width=5, bg="#34495e", fg="#ecf0f1",
                            relief="flat", bd=0, highlightthickness=0, activebackground="#2980b9", activeforeground="#ecf0f1",
                            command=lambda i=i: self.make_move(i))
            btn.grid(row=i // 3, column=i % 3, padx=5, pady=5)

    def make_move(self, index):
        if self.game.board[index] is None: # if the choosen cell is empty
            self.game.make_move(index)
            self.show_board()  # Update the board immediately after the move.
            if self.game.check_winner():
                result = f"{self.game.players[1 - self.game.current_player]['name']} wins!"
                self.save_and_show_result(result)
            elif self.game.is_draw():
                result = "It's a draw!"
                self.save_and_show_result(result)

    def save_and_show_result(self, result):
        current_time = datetime.now().strftime('%H:%M')
        game_data = (
            self.game.players[0]["name"], self.game.players[0]["symbol"],
            self.game.players[1]["name"], self.game.players[1]["symbol"],
            result, current_time
        )
        self.db_manager.save_game(game_data)
        messagebox.showinfo("Game Over", result)
        self.create_main_menu()

    def update(self, event, data):
        if event == "move_made":
            self.show_board()  # Update the board when a move is made

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    connection = mysql.connector.connect(
        host="localhost",
        user="abdo",
        password="0000",
        database="game"
    )
    db_manager = DatabaseManager(connection)
    db_manager.create_table()

    game = TicTacToeGame()
    gui = TicTacToeGUI(game, db_manager)
    gui.run()
