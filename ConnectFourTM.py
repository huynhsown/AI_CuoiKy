import threading
import time
import numpy as np
from easyAI import Negamax
from TwoPlayers import TwoPlayerGame
import pygame
from Players import *
from constains import *
import sys
from button import *

pygame.init()
pygame.display.set_caption("Connect Four Classic")
pygame.display.set_icon(pygame.image.load("./Resources/Images/logo.png"))
DROP_SOUND = pygame.mixer.Sound("./Resources/Sounds/DropItem.mp3")
WIN_SOUND = pygame.mixer.Sound("./Resources/Sounds/Win.mp3")
CLICK_OPTION_SOUND = pygame.mixer.Sound("./Resources/Sounds/ClickOption.mp3")
LOSS_SOUND = pygame.mixer.Sound("./Resources/Sounds/Loss.mp3")
OPTION_SIZE = 45
AI_DEPTH = 5
players = [Human_Player(), AI_Player(Negamax(AI_DEPTH))]


class GameController(TwoPlayerGame):
    def __init__(self, board=None):
        self.players = players
        self.board = board if (board is not None) else np.array([[0 for _ in range(width)] for _ in range(height)])
        self.current_player = 1
        self.pos_dir = np.array([[[i, 0], [0, 1]] for i in range(height)] +
                                [[[0, i], [1, 0]] for i in range(width)] +
                                [[[i, 0], [1, 1]] for i in range(1, 3)] +
                                [[[0, i], [1, 1]] for i in range(4)] +
                                [[[i, height], [1, -1]] for i in range(1, 3)] +
                                [[[0, i], [1, -1]] for i in range(3, width)])
        self.ai_turn = False

    def possible_moves(self):
        return [i for i in range(width) if self.board[:, i].min() == 0]

    def make_move(self, column):
        line = np.argmin(self.board[:, column] != 0)
        self.board[line, column] = self.current_player

    def loss_condition(self):
        for pos, direction in self.pos_dir:
            streak = 0
            while (0 <= pos[0] < ROWS) and (0 <= pos[1] < COLS):
                if self.board[pos[0], pos[1]] == self.opponent_index:
                    streak += 1
                    if streak == len_win:
                        return True
                else:
                    streak = 0
                pos = pos + direction
        return False

    def is_over(self):
        return (self.board.min() > 0) or self.loss_condition()

    def scoring(self):
        return -100 if self.loss_condition() else 0

    def reset(self):
        self.__init__()


class GameView:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    def check_in_circle(self, pos):
        row = pos[1] // (SCREEN_HEIGHT // ROWS)
        col = pos[0] // (SCREEN_WIDTH // COLS)
        x = (col + 1) * (SCREEN_WIDTH // (COLS + 1))
        y = (row + 1) * (SCREEN_HEIGHT // (ROWS + 1))
        distance = ((x - pos[0]) ** 2 + (y - pos[1]) ** 2) ** 0.5
        if distance <= CIRCLE_RADIUS:
            return row, col
        return None

    def get_font(self, size):
        return pygame.font.Font("./Resources/Fonts/Crang.ttf", size)

    def menu_screen(self, Game):
        while True:
            self.screen.fill(BG_COLOR)
            MENU_MOUSE_POS = pygame.mouse.get_pos()
            paused_text = self.get_font(80).render("CONNECT FOUR", True, WIN)
            text_rect = paused_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 // 3))
            self.screen.blit(paused_text, text_rect)

            PLAY_BUTTON = Button(pos=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2.8),
                                 text_input="PLAY", font=self.get_font(OPTION_SIZE), base_color=BASE_COLOR, hovering_color="White")
            QUIT_BUTTON = Button(pos=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 1.5),
                                 text_input="QUIT", font=self.get_font(OPTION_SIZE), base_color=BASE_COLOR, hovering_color="White")

            GUIDE_BUTTON = Button(pos=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2),
                                 text_input="GUIDE", font=self.get_font(OPTION_SIZE), base_color=BASE_COLOR,
                                 hovering_color="White")

            for button in [PLAY_BUTTON, GUIDE_BUTTON, QUIT_BUTTON]:
                button.changeColor(MENU_MOUSE_POS)
                button.update(self.screen)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if PLAY_BUTTON.checkForInput(MENU_MOUSE_POS):
                        CLICK_OPTION_SOUND.play()
                        Game.play_game()
                    elif GUIDE_BUTTON.checkForInput(MENU_MOUSE_POS):
                        CLICK_OPTION_SOUND.play()
                        self.guide()
                    elif QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                        CLICK_OPTION_SOUND.play()
                        time.sleep(0.4)
                        pygame.quit()
                        sys.exit()

            pygame.display.update()

    def guide(self):
        running = True
        while running:
            self.screen.fill(BG_COLOR)
            MENU_MOUSE_POS = pygame.mouse.get_pos()

            # Văn bản hướng dẫn
            text_lines = [
                "Connect Four is a game where the objective is to place four of your own tokens",
                "consecutively either horizontally, vertically, or diagonally on the game board.",
                "The first player to achieve this is the winner.",
                "Press SPACE to pause."
            ]
            font = self.get_font(15)
            line_height = 40
            for i, line in enumerate(text_lines):
                text_surface = font.render(line, True, WIN)
                text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3 + i * line_height))
                self.screen.blit(text_surface, text_rect)

            BACK_BUTTON = Button(pos=(SCREEN_WIDTH // 10, SCREEN_HEIGHT // 20),
                                  text_input="BACK TO MENU", font=self.get_font(20), base_color=BASE_COLOR,
                                  hovering_color="White")

            for button in [BACK_BUTTON]:
                button.changeColor(MENU_MOUSE_POS)
                button.update(self.screen)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if BACK_BUTTON.checkForInput(MENU_MOUSE_POS):
                        CLICK_OPTION_SOUND.play()
                        running = False

            pygame.display.update()

    def draw_grid(self, board):
        self.screen.fill(BG_COLOR)
        for row in range(ROWS):
            for col in range(COLS):
                x = (col + 1) * (SCREEN_WIDTH // (COLS + 1))
                y = (row + 1) * (SCREEN_HEIGHT // (ROWS + 1))
                player = board[ROWS - row - 1][col]
                color = player == 0 and WHITE or (player == 1 and BLUE or RED)
                pygame.draw.circle(self.screen, color, (x, y), CIRCLE_RADIUS)
        pygame.display.update()

    def animate_circle(self, column, row, color):
        for i in range(row + 1):
            x = (column + 1) * (SCREEN_WIDTH // (COLS + 1))
            y = (i + 1) * (SCREEN_HEIGHT // (ROWS + 1))
            pygame.draw.circle(self.screen, color, (x, y), CIRCLE_RADIUS)
            pygame.display.update()
            DROP_SOUND.play()
            time.sleep(0.1)
            if i != row:
                time.sleep(0)
                pygame.draw.circle(self.screen, WHITE, (x, y), CIRCLE_RADIUS)
                pygame.display.update()

    def fill_circle(self, board, column, color):
        index = np.argmax(board[:, column] == 0)
        row = ROWS - index if (index != 0) else 0
        animation_thread = threading.Thread(target=self.animate_circle, args=(column, row, color))
        animation_thread.start()
        animation_thread.join()

    def reset_game(self, GameController, Game):
        player = GameController.opponent_index
        if player == 1:
            WIN_SOUND.play()
        else:
            LOSS_SOUND.play()
        time.sleep(0.3)
        gameover = True
        GameController.reset()
        while gameover:
            self.screen.fill(BG_COLOR)
            MENU_MOUSE_POS = pygame.mouse.get_pos()
            win_text = self.get_font(80).render(player == 1 and "Player Win" or "Bot Win", True, WIN)
            text_rect = win_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 // 3))
            self.screen.blit(win_text, text_rect)

            NEW_GAME_BUTTON = Button(pos=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2.8),
                                 text_input="NEW GAME", font=self.get_font(OPTION_SIZE), base_color=BASE_COLOR,
                                 hovering_color=WHITE)
            BACK_BUTTON = Button(pos=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 1.8),
                                 text_input="BACK TO MENU", font=self.get_font(OPTION_SIZE), base_color=BASE_COLOR,
                                 hovering_color=WHITE)

            for button in [NEW_GAME_BUTTON, BACK_BUTTON]:
                button.changeColor(MENU_MOUSE_POS)
                button.update(self.screen)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if NEW_GAME_BUTTON.checkForInput(MENU_MOUSE_POS):
                        CLICK_OPTION_SOUND.play()
                        self.draw_grid(GameController.board)
                        gameover = False
                    elif BACK_BUTTON.checkForInput(MENU_MOUSE_POS):
                        CLICK_OPTION_SOUND.play()
                        return 1

            pygame.display.update()

    def pause(self, GameController):
        paused = True
        while paused:
            self.screen.fill(BG_COLOR)
            MENU_MOUSE_POS = pygame.mouse.get_pos()
            paused_text = self.get_font(80).render("PAUSED", True, WIN)
            text_rect = paused_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 // 3))
            self.screen.blit(paused_text, text_rect)

            RESUME_BUTTON = Button(pos=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2.8),
                                     text_input="RESUME", font=self.get_font(OPTION_SIZE), base_color=BASE_COLOR,
                                     hovering_color=WHITE)
            BACK_BUTTON = Button(pos=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 1.8),
                                 text_input="BACK TO MENU", font=self.get_font(OPTION_SIZE), base_color=BASE_COLOR,
                                 hovering_color=WHITE)

            for button in [RESUME_BUTTON, BACK_BUTTON]:
                button.changeColor(MENU_MOUSE_POS)
                button.update(self.screen)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if RESUME_BUTTON.checkForInput(MENU_MOUSE_POS):
                        CLICK_OPTION_SOUND.play()
                        return 0
                    if BACK_BUTTON.checkForInput(MENU_MOUSE_POS):
                        CLICK_OPTION_SOUND.play()
                        GameController.reset()
                        self.draw_grid(GameController.board)
                        return 1
            pygame.display.update()


class Game:
    def __init__(self):
        self.controller = GameController()
        self.view = GameView()

    def play_game(self):
        self.view.draw_grid(self.controller.board)
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        c = self.view.pause(self.controller)
                        if c == 0:
                            self.view.draw_grid(self.controller.board)
                        if c == 1:
                            running = False
                            break

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if not self.controller.is_over():
                        pos = self.view.check_in_circle(pygame.mouse.get_pos())
                        if pos is None:
                            continue
                        if self.controller.current_player == 1:
                            move = pos[1]
                            self.controller.make_move(move)
                            self.view.fill_circle(self.controller.board, move, BLUE)
                            self.controller.switch_player()
                            self.controller.ai_turn = True

            if not self.controller.is_over() and self.controller.ai_turn:
                move = self.controller.player.ask_move(self.controller)
                self.controller.make_move(move)
                self.view.fill_circle(self.controller.board, move, RED)
                self.controller.switch_player()
                self.controller.ai_turn = False

            if self.controller.is_over():
                if self.view.reset_game(self.controller, self) == 1:
                    running = False

            pygame.display.update()

    def run(self):
        self.view.menu_screen(self)


if __name__ == '__main__':
    Game().run()
