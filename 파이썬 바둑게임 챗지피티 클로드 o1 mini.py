import tkinter as tk

class GoBoard:
    def __init__(self, master, board_size):
        self.master = master
        self.master.title("Go Board")
        self.board_size = 19
        self.cell_size = board_size // self.board_size
        self.board = [[' ' for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.move_history = {}
        self.current_player = 'B'
        self.move_number = 0
        self.ko_point = None

        # Allow window resizing (해상도 고정)
        self.master.resizable(width=False, height=False)

        self.canvas = tk.Canvas(self.master, width=board_size, height=board_size, bg='#DEB887')
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.master.rowconfigure(0, weight=1)
        self.master.columnconfigure(0, weight=1)

        # Frame for status and restart button
        bottom_frame = tk.Frame(self.master)
        bottom_frame.grid(row=1, column=0, sticky="ew")

        self.status_var = tk.StringVar()
        self.status_label = tk.Label(bottom_frame, textvariable=self.status_var, font=('Arial', 18))
        self.status_label.grid(row=0, column=0, padx=20, pady=10)

        # Restart Button with black border
        self.restart_button = tk.Button(
            bottom_frame, text="Restart Game", command=self.restart_game,
            font=('Arial', 14), relief="solid", borderwidth=2,
            highlightbackground="black", highlightcolor="black"
        )
        self.restart_button.grid(row=0, column=1, padx=20, pady=10)

        # Center alignment for both widgets
        bottom_frame.columnconfigure(0, weight=1)
        bottom_frame.columnconfigure(1, weight=1)

        self.update_status()
        self.draw_board_background()
        self.canvas.bind('<Button-1>', self.place_stone)

    def draw_board_background(self):
        """Draw the static parts of the board: grid and star points."""
        self.canvas.delete("background")
        for i in range(self.board_size):
            self.canvas.create_line(
                self.cell_size / 2, i * self.cell_size + self.cell_size / 2,
                self.board_size * self.cell_size - self.cell_size / 2, i * self.cell_size + self.cell_size / 2,
                tags="background"
            )
            self.canvas.create_line(
                i * self.cell_size + self.cell_size / 2, self.cell_size / 2,
                i * self.cell_size + self.cell_size / 2, self.board_size * self.cell_size - self.cell_size / 2,
                tags="background"
            )

        star_points = [(3, 3), (3, 9), (3, 15), (9, 3), (9, 9), (9, 15), (15, 3), (15, 9), (15, 15)]
        for (x, y) in star_points:
            self.canvas.create_oval(
                (x + 0.5) * self.cell_size - 5, (y + 0.5) * self.cell_size - 5,
                (x + 0.5) * self.cell_size + 5, (y + 0.5) * self.cell_size + 5,
                fill='black', tags="background"
            )

    def place_stone(self, event):
        col = round((event.x - self.cell_size / 2) / self.cell_size)
        row = round((event.y - self.cell_size / 2) / self.cell_size)

        if 0 <= row < self.board_size and 0 <= col < self.board_size and self.board[row][col] == ' ':
            if self.is_valid_move(row, col):
                self.board[row][col] = self.current_player
                self.move_number += 1
                self.move_history[(row, col)] = self.move_number

                color = 'black' if self.current_player == 'B' else 'white'
                self.draw_stone(row, col, color)
                self.draw_move_number(row, col)

                captured = self.remove_captured_stones(row, col)
                self.update_ko(row, col, captured)

                if self.check_for_win():
                    self.status_var.set(f"Player {self.current_player} wins!")
                    self.canvas.unbind('<Button-1>')
                else:
                    self.current_player = 'W' if self.current_player == 'B' else 'B'
                    self.update_status()
            else:
                self.status_var.set("Invalid move. Try again.")

    def is_valid_move(self, row, col):
        if (row, col) == self.ko_point:
            return False

        # Check for self-capture
        self.board[row][col] = self.current_player
        has_liberty = self.has_liberty(row, col)
        self.board[row][col] = ' '

        if not has_liberty:
            # Check if this move captures opponent's stones
            for d_row, d_col in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                n_row, n_col = row + d_row, col + d_col
                if 0 <= n_row < self.board_size and 0 <= n_col < self.board_size:
                    if self.board[n_row][n_col] != self.current_player and self.board[n_row][n_col] != ' ':
                        if not self.has_liberty(n_row, n_col):
                            return True
            return False

        return True

    def draw_stone(self, row, col, color):
        self.canvas.create_oval(
            col * self.cell_size + 2, row * self.cell_size + 2,
            (col + 1) * self.cell_size - 2, (row + 1) * self.cell_size - 2,
            fill=color, outline=color, tags=(f"stone_{row}_{col}", "stone")
        )

    def draw_move_number(self, row, col):
        move_number = self.move_history[(row, col)]
        color = 'black' if self.board[row][col] == 'W' else 'white'
        font_size = int(self.cell_size // 3)
        self.canvas.create_text(
            col * self.cell_size + self.cell_size // 2,
            row * self.cell_size + self.cell_size // 2,
            text=str(move_number), fill=color,
            font=('Arial', font_size, 'bold'),
            tags=(f"move_number_{row}_{col}", "move_number")
        )

    def update_status(self):
        self.status_var.set(f"Current Player: {'Black' if self.current_player == 'B' else 'White'}")

    def check_for_win(self):
        for row in range(self.board_size):
            for col in range(self.board_size):
                if self.board[row][col] == ' ':
                    return False
        return True

    def restart_game(self):
        self.board = [[' ' for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.move_history.clear()
        self.current_player = 'B'
        self.move_number = 0
        self.ko_point = None
        self.canvas.delete("stone")        # Deletes all items with the "stone" tag
        self.canvas.delete("move_number")  # Deletes all items with the "move_number" tag
        self.update_status()
        self.draw_board_background()        # Redraw the board grid and star points
        self.canvas.bind('<Button-1>', self.place_stone)

    def remove_captured_stones(self, row, col):
        captured = []
        for d_row, d_col in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            n_row, n_col = row + d_row, col + d_col
            if 0 <= n_row < self.board_size and 0 <= n_col < self.board_size:
                if self.board[n_row][n_col] != self.current_player and self.board[n_row][n_col] != ' ':
                    if not self.has_liberty(n_row, n_col):
                        captured.extend(self.remove_group(n_row, n_col))
        return captured

    def has_liberty(self, row, col):
        color = self.board[row][col]
        queue = [(row, col)]
        visited = set()
        while queue:
            r, c = queue.pop(0)
            if (r, c) in visited:
                continue
            visited.add((r, c))
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.board_size and 0 <= nc < self.board_size:
                    if self.board[nr][nc] == ' ':
                        return True
                    elif self.board[nr][nc] == color and (nr, nc) not in visited:
                        queue.append((nr, nc))
        return False

    def remove_group(self, row, col):
        color = self.board[row][col]
        queue = [(row, col)]
        to_remove = []
        while queue:
            r, c = queue.pop(0)
            if (r, c) in to_remove:
                continue
            to_remove.append((r, c))
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.board_size and 0 <= nc < self.board_size and self.board[nr][nc] == color:
                    queue.append((nr, nc))
        for r, c in to_remove:
            self.board[r][c] = ' '
            self.canvas.delete(f"stone_{r}_{c}")
            self.canvas.delete(f"move_number_{r}_{c}")
            if (r, c) in self.move_history:
                del self.move_history[(r, c)]
        return to_remove

    def update_ko(self, row, col, captured):
        if len(captured) == 1 and len(self.get_adjacent_points(row, col)) == 1:
            self.ko_point = captured[0]
        else:
            self.ko_point = None

    def get_adjacent_points(self, row, col):
        adjacent = []
        for d_row, d_col in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            n_row, n_col = row + d_row, col + d_col
            if 0 <= n_row < self.board_size and 0 <= n_col < self.board_size:
                if self.board[n_row][n_col] == self.current_player:
                    adjacent.append((n_row, n_col))
        return adjacent

def select_resolution():
    resolution_window = tk.Tk()
    resolution_window.title("Select Resolution")

    def set_resolution(size):
        resolution_window.selected_size = size
        resolution_window.destroy()

    tk.Label(resolution_window, text="Choose board resolution:", font=('Arial', 14)).pack(pady=20)
    tk.Button(resolution_window, text="800 x 800", font=('Arial', 14), command=lambda: set_resolution(800)).pack(pady=10)
    tk.Button(resolution_window, text="1600 x 1600", font=('Arial', 14), command=lambda: set_resolution(1600)).pack(pady=10)

    resolution_window.mainloop()
    return resolution_window.selected_size

if __name__ == "__main__":
    selected_size = select_resolution()  # 사용자 해상도 선택
    root = tk.Tk()
    go_board = GoBoard(root, selected_size)
    root.mainloop()
