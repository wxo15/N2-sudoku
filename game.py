import pygame
import time
import csv
import datetime


class Grid:

    def __init__(self, mode, width, height, win, valid_range):
        self.rows = mode * mode
        self.cols = mode * mode
        self.mode = mode
        self.valid_range = valid_range
        with open('board' + str(mode) + '.csv', 'r') as read_obj:
            # pass the file object to reader() to get the reader object
            csv_reader = csv.reader(read_obj)
            # Pass reader object to list() to get a list of lists
            board = list(csv_reader)
        for i in range(mode*mode):
            for j in range(mode*mode):
                if board[i][j].isnumeric():
                    board[i][j] = int(board[i][j])
        self.cubes = [[Cube(mode, board[i][j], i, j, width, height) for j in range(mode * mode)] for i in range(mode * mode)]
        self.width = width
        self.height = height
        self.model = None
        self.update_model()
        self.selected = None
        self.win = win

    def update_model(self):
        self.model = [[self.cubes[i][j].value for j in range(self.cols)] for i in range(self.rows)]

    def place(self, val):
        row, col = self.selected
        if self.cubes[row][col].value == 0:
            self.cubes[row][col].set(val)
            self.update_model()

            if valid(self.model, val, (row, col), self.mode) and self.solve():
                return True
            else:
                self.cubes[row][col].set(0)
                self.cubes[row][col].set_temp(0)
                self.update_model()
                return False

    def sketch(self, val):
        row, col = self.selected
        self.cubes[row][col].set_temp(val)

    def draw(self):
        # Draw Grid Lines
        gap = self.width / (self.mode * self.mode)
        for i in range(self.rows+1):
            if i % self.mode == 0 and i != 0:
                thick = 4
            else:
                thick = 1
            pygame.draw.line(self.win, (0, 0, 0), (0, i*gap), (self.width, i*gap), thick)
            pygame.draw.line(self.win, (0, 0, 0), (i * gap, 0), (i * gap, self.height), thick)

        # Draw Cubes
        for i in range(self.rows):
            for j in range(self.cols):
                self.cubes[i][j].draw(self.win)

    def select(self, row, col):
        # Reset all other
        for i in range(self.rows):
            for j in range(self.cols):
                self.cubes[i][j].selected = False
        self.cubes[row][col].selected = True
        self.selected = (row, col)

    def clear(self):
        if self.selected is not None:
            row, col = self.selected
            if self.cubes[row][col].value == 0:
                self.cubes[row][col].set_temp(0)

    def click(self, pos):
        if pos[0] < self.width and pos[1] < self.height:
            gap = self.width / (self.mode * self.mode)
            x = pos[0] // gap
            y = pos[1] // gap
            return int(y), int(x)
        else:
            return None

    def is_finished(self):
        for i in range(self.rows):
            for j in range(self.cols):
                if self.cubes[i][j].value == 0:
                    return False
        return True

    def solve(self):
        find = find_empty(self.model)
        if not find:
            return True
        else:
            row, col = find
        for i in self.valid_range:
            if valid(self.model, i, (row, col), self.mode):
                self.model[row][col] = i
                if self.solve():
                    return True
                self.model[row][col] = 0
        return False

    def solve_gui(self):
        self.update_model()
        find = find_empty(self.model)
        if not find:
            return True
        else:
            row, col = find
        for i in self.valid_range:
            if valid(self.model, i, (row, col), self.mode):
                self.model[row][col] = i
                self.cubes[row][col].set(i)
                self.cubes[row][col].draw_change(self.win, True)
                self.update_model()
                pygame.display.update()
                pygame.time.delay(10)
                if self.solve_gui():
                    return True
                self.model[row][col] = 0
                self.cubes[row][col].set(0)
                self.update_model()
                self.cubes[row][col].draw_change(self.win, False)
                pygame.display.update()
                pygame.time.delay(10)
        return False


class Cube:

    def __init__(self, mode, value, row, col, width, height):
        self.mode = mode
        self.value = value
        self.temp = 0
        self.row = row
        self.col = col
        self.width = width
        self.height = height
        self.selected = False

    def draw(self, win):
        fnt = pygame.font.SysFont('Calibri', 40, True, False)
        gap = self.width / (self.mode * self.mode)
        x = self.col * gap
        y = self.row * gap
        if self.temp != 0 and self.value == 0:
            text = fnt.render(str(self.temp), True, (128, 128, 128))
            win.blit(text, (x + (gap / 2 - text.get_width() / 2), y + (gap / 2 - text.get_height() / 2)))
        elif not(self.value == 0):
            text = fnt.render(str(self.value), True, (0, 0, 0))
            win.blit(text, (x + (gap / 2 - text.get_width() / 2), y + (gap / 2 - text.get_height() / 2)))
        if self.selected:
            pygame.draw.rect(win, (255, 0, 0), (x, y, gap, gap), 3)

    def draw_change(self, win, status=True):
        fnt = pygame.font.SysFont('Calibri', 40, True, False)
        gap = self.width / (self.mode * self.mode)
        x = self.col * gap
        y = self.row * gap
        pygame.draw.rect(win, (255, 255, 255), (x, y, gap, gap), 0)
        text = fnt.render(str(self.value), True, (0, 0, 0))
        win.blit(text, (x + (gap / 2 - text.get_width() / 2), y + (gap / 2 - text.get_height() / 2)))
        if status:
            pygame.draw.rect(win, (0, 255, 0), (x, y, gap, gap), 3)
        else:
            pygame.draw.rect(win, (255, 0, 0), (x, y, gap, gap), 3)

    def set(self, val):
        self.value = val

    def set_temp(self, val):
        self.temp = val


def find_empty(board):
    for i in range(len(board)):
        for j in range(len(board[0])):
            if board[i][j] == 0:
                return i, j  # row, col

    return None


def valid(board, num, pos, mode):
    # Check row
    for i in range(len(board[0])):
        if board[pos[0]][i] == num and pos[1] != i:
            return False

    # Check column
    for i in range(len(board)):
        if board[i][pos[1]] == num and pos[0] != i:
            return False

    # Check box
    start_x = pos[1] - pos[1] % mode
    start_y = pos[0] - pos[0] % mode

    for i in range(mode):
        for j in range(mode):
            if board[i + start_y][j + start_x] == num and (i + start_y, j + start_x) != pos:
                return False
    return True


def redraw_window(win, board, time, lives, heart_img, state=None):
    w, h = pygame.display.get_surface().get_size()
    win.fill((255, 255, 255))
    # Draw time
    fnt = pygame.font.SysFont('Calibri', 40, True, False)
    text = fnt.render(str(datetime.timedelta(seconds=time)), True, (0, 0, 0))
    win.blit(text, (w - text.get_rect().width, h - text.get_rect().height))
    # Draw state
    if state is not None:
        if state == "-1":
            text_game_over = fnt.render("Game Over", True, (255, 0, 0))
        if state == "1":
            text_game_over = fnt.render("Finish!", True, (0, 255, 0))
        win.blit(text_game_over, (w / 2 - text_game_over.get_rect().width / 2, h / 2 - text_game_over.get_rect().height / 2))
        text_end_game = fnt.render("Esc to quit", True, (0, 0, 0))
        win.blit(text_end_game, (w / 2 - text_end_game.get_rect().width / 2, h / 2 + text_end_game.get_rect().height / 2))
    # Draw Lives using Hearts
    for i in range(lives + 1):
        win.blit(heart_img, ((i - 1) * heart_img.get_rect().width, h - heart_img.get_rect().height))
    # Draw grid and board
    board.draw()


def main():
    # Mode Selection for N2 Sudoku. Tested up to 5.
    n2mode = 4

    # Import heart image
    heart_img = pygame.image.load('heart.svg')

    # Valid range. Contains N^2 unique inputs.
    if n2mode == 2:
        valid_range = [1, 2, 3, 4]
    else:
        valid_range = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        if n2mode > 3:
            i = 9
            while i < n2mode*n2mode:
                # This takes ascii characters until the required number of elements is satisfied, starting from 'a'
                valid_range.append(chr(88 + i))
                i += 1

    # Make a pygame display
    win_width = 60 * n2mode * n2mode
    win_height = 60 * (n2mode * n2mode + 1)
    win = pygame.display.set_mode((win_width, win_height))
    pygame.display.set_caption("N2 Sudoku")

    # Make a board
    board = Grid(n2mode, win_width, win_width, win, valid_range)

    # Set up game variables.
    # Key: input characters. Run: Keep screen up. State: is not none to show pop-ups. Strike: 0.
    key = None
    run = True
    state = None
    start_time = time.time()
    lives = 3

    # Run
    while run:
        play_time = round(time.time() - start_time)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            # Set up valid input characters
            if event.type == pygame.KEYDOWN:
                if n2mode > 1:
                    if event.key == pygame.K_1 or event.key == pygame.K_KP1:
                        key = 1
                    if event.key == pygame.K_2 or event.key == pygame.K_KP2:
                        key = 2
                    if event.key == pygame.K_3 or event.key == pygame.K_KP3:
                        key = 3
                    if event.key == pygame.K_4 or event.key == pygame.K_KP4:
                        key = 4
                if n2mode > 2:
                    if event.key == pygame.K_5 or event.key == pygame.K_KP5:
                        key = 5
                    if event.key == pygame.K_6 or event.key == pygame.K_KP6:
                        key = 6
                    if event.key == pygame.K_7 or event.key == pygame.K_KP7:
                        key = 7
                    if event.key == pygame.K_8 or event.key == pygame.K_KP8:
                        key = 8
                    if event.key == pygame.K_9 or event.key == pygame.K_KP9:
                        key = 9
                if n2mode > 3:
                    if event.key == pygame.K_a:
                        key = 'a'
                    if event.key == pygame.K_b:
                        key = 'b'
                    if event.key == pygame.K_c:
                        key = 'c'
                    if event.key == pygame.K_d:
                        key = 'd'
                    if event.key == pygame.K_e:
                        key = 'e'
                    if event.key == pygame.K_f:
                        key = 'f'
                    if event.key == pygame.K_g:
                        key = 'g'
                if n2mode > 4:
                    if event.key == pygame.K_h:
                        key = 'h'
                    if event.key == pygame.K_i:
                        key = 'i'
                    if event.key == pygame.K_j:
                        key = 'j'
                    if event.key == pygame.K_k:
                        key = 'k'
                    if event.key == pygame.K_l:
                        key = 'l'
                    if event.key == pygame.K_m:
                        key = 'm'
                    if event.key == pygame.K_n:
                        key = 'n'
                    if event.key == pygame.K_o:
                        key = 'o'
                    if event.key == pygame.K_p:
                        key = 'p'
                if event.key == pygame.K_SPACE:
                    board.solve_gui()
                if event.key == pygame.K_DELETE:
                    board.clear()
                    key = None
                if event.key == pygame.K_RETURN:
                    i, j = board.selected
                    if board.cubes[i][j].temp != 0:
                        if board.place(board.cubes[i][j].temp):
                            print("Right")
                        else:
                            print("Wrong")
                            lives -= 1
                        key = None
                if event.key == pygame.K_ESCAPE and state is not None:
                    run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                clicked = board.click(pos)
                if clicked:
                    board.select(clicked[0], clicked[1])
                    key = None
        if board.selected and key is not None:
            board.sketch(key)
        if board.is_finished():
            state = "1"
        if lives == 0:
            state = "-1"
        redraw_window(win, board, play_time, lives, heart_img, state)
        pygame.display.update()


pygame.init()
main()
pygame.quit()
