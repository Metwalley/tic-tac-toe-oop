import os

def clear_screen():
    # Clears the terminal screen for better user experience
    os.system("cls" if os.name == "nt" else "clear")

class Player:
    def __init__(self):
        self.name = ""
        self.symbol = ''

    def choose_name(self):
        while True:
            name = input("Enter Your Name (Letters Only): ")
            if name.isalpha():  # Ensure the name contains only letters
                self.name = name
                break
            print("Invalid name. Please enter letters only.")

    def choose_symbol(self):
        while True:
            symbol = input(f"{self.name}, Enter Your Symbol (One Letter Only): ")
            if symbol.isalpha() and len(symbol) == 1:  # Ensure a single letter
                self.symbol = symbol.upper()
                break
            print("Invalid symbol. Please enter one letter.")

class Menu:
    def display_main_menu(self):
        print("Welcome to my Tic Tac Toe!")
        print("1. Start Game")
        print("2. Quit Game")
        choice = input("Enter your choice (1 or 2): ")
        return self.check_choice(choice)

    def display_end_menu(self):
        print("\nGAME OVER!")
        print("1. Restart Game")
        print("2. Quit Game")
        choice = input("Enter your choice (1 or 2): ")
        return self.check_choice(choice)

    def check_choice(self, choice):
        while choice not in ("1", "2"):  # Ensure valid menu input
            choice = input("Please enter a correct choice (1 or 2): ")
        return choice

class Board:
    def __init__(self):
        self.board = [str(i) for i in range(1, 10)]  # Create a 3x3 board with numbers

    def display_board(self):
        # Display the board in a grid format
        for i in range(0, 9, 3):  # Iterates through rows (0-2, 3-5, 6-8)
            print(" | ".join(self.board[i:i+3]))
            if i < 6:  # Avoid printing the divider after the last row
                print("-" * 9)

    def update_board(self, choice, symbol):
        # Update the board if the chosen cell is valid
        if self.check_valid(choice):
            self.board[choice - 1] = symbol
            return True
        return False

    def reset_board(self):
        # Resets the board to its initial state
        self.board = [str(i) for i in range(1, 10)]

    def check_valid(self, choice):
        # Check if the cell is not already taken
        return self.board[choice - 1].isdigit()

class Game:
    def __init__(self):
        self.players = [Player(), Player()]
        self.board = Board()
        self.menu = Menu()
        self.current_player_index = 0

    def start_game(self):
        choice = self.menu.display_main_menu()
        if choice == "1":
            self.setup_players()
            self.play_round()
        else:
            self.quit_game()

    def play_turn(self):
        # Manage a single player's turn
        player = self.players[self.current_player_index]
        self.board.display_board()
        print(f"{player.name}'s turn ({player.symbol})")
        while True:
            try:
                cell_choice = int(input("Choose a cell (1 to 9): "))
                if cell_choice in range(1, 10) and self.board.update_board(cell_choice, player.symbol):
                    break
                print("Invalid move. Try again.")
            except ValueError:
                print("Please enter a number between 1 and 9.")
        self.switch_player()
        clear_screen()

    def check_win(self):
        # Check if a player has won
        winning_combos = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Rows
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Columns
            [0, 4, 8], [2, 4, 6]  # Diagonals
        ]
        for combo in winning_combos:
            if (self.board.board[combo[0]] == self.board.board[combo[1]] == self.board.board[combo[2]]):
                # Return True and the previous player's name (who played before the switch)
                return True, self.players[self.current_player_index - 1].name
        return False, None

    def check_draw(self):
        # A draw occurs if no cells are available and no winner exists
        return all(not cell.isdigit() for cell in self.board.board)

    def restart_game(self):
        # Reset the game state for a new round
        self.board.reset_board()
        self.current_player_index = 0
        self.play_round()

    def quit_game(self):
        print("See you later!")

    def setup_players(self):
        # Gather player details
        for number, player in enumerate(self.players, start=1):
            print(f"Player {number}, enter your details:")
            player.choose_name()
            player.choose_symbol()
            clear_screen()

    def play_round(self):
        # Manage the gameplay loop
        while True:
            self.play_turn()
            win, winner_name = self.check_win()
            if win:
                self.board.display_board()
                print(f"Congratulations! {winner_name} wins!")
                choice = self.menu.display_end_menu()
                if choice == "1":
                    self.restart_game()
                else:
                    self.quit_game()
                break
            elif self.check_draw():
                self.board.display_board()
                print("It's a draw!")
                choice = self.menu.display_end_menu()
                if choice == "1":
                    self.restart_game()
                else:
                    self.quit_game()
                break

    def switch_player(self):
        # Toggle between player 0 and 1
        self.current_player_index = 1 - self.current_player_index

game = Game()
game.start_game()
