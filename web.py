import streamlit as st
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

# Constants
ROWS = 6
COLS = 7
AI_DEPTH = 5
CIRCLE_RADIUS = 30
WHITE = "#FFFFFF"
BLUE = "#0000FF"
RED = "#FF0000"

class ConnectFour(TwoPlayerGame):
    def __init__(self, players):
        self.board = np.zeros((ROWS, COLS), dtype=int)
        self.players = players
        self.current_player = 1

    def possible_moves(self):
        return [i for i in range(COLS) if self.board[:, i].min() == 0]

    def make_move(self, column):
        row = np.argmin(self.board[:, column] != 0)
        self.board[row, column] = self.current_player

    def unmake_move(self, column):
        row = max([r for r in range(ROWS) if self.board[r, column] != 0])
        self.board[row, column] = 0

    def lose(self):
        for r in range(ROWS):
            for c in range(COLS):
                if self.board[r, c] == self.current_player:
                    if self.is_winner(r, c):
                        return True
        return False

    def is_winner(self, row, col):
        player = self.board[row, col]
        for dr, dc in [(1, 0), (0, 1), (1, 1), (1, -1)]:
            count = 0
            for i in range(-3, 4):
                r, c = row + dr * i, col + dc * i
                if 0 <= r < ROWS and 0 <= c < COLS and self.board[r, c] == player:
                    count += 1
                    if count == 4:
                        return True
                else:
                    count = 0
        return False

    def is_over(self):
        return self.lose() or (self.possible_moves() == [])

    def show(self):
        print(self.board[::-1])

    def scoring(self):
        return -100 if self.lose() else 0

def draw_grid(board):
    for row in range(ROWS):
        cols = st.columns(COLS)
        for col in range(COLS):
            cell = cols[col]
            player = board[ROWS - row - 1][col]
            color = WHITE if player == 0 else (BLUE if player == 1 else RED)
            cell.button(" ", key=f"{row}-{col}", on_click=make_move, args=(col,), disabled=(player != 0))
            cell.markdown(f"<div style='background-color:{color}; height: 50px; width: 50px; border-radius: 50%;'></div>", unsafe_allow_html=True)

def make_move(column):
    if st.session_state.game.current_player == 1:
        st.session_state.game.make_move(column)
        if st.session_state.game.is_over():
            st.session_state.winner = st.session_state.game.current_player
        else:
            st.session_state.game.switch_player()
            st.session_state.ai_turn = True
    if st.session_state.ai_turn:
        move = st.session_state.game.players[1].ask_move(st.session_state.game)
        st.session_state.game.make_move(move)
        if st.session_state.game.is_over():
            st.session_state.winner = st.session_state.game.current_player
        else:
            st.session_state.game.switch_player()
            st.session_state.ai_turn = False

def reset_game():
    st.session_state.game = ConnectFour([Human_Player(), AI_Player(Negamax(AI_DEPTH))])
    st.session_state.winner = None
    st.session_state.ai_turn = False

def main():
    st.title("Connect Four Classic")

    if "game" not in st.session_state:
        reset_game()

    if st.session_state.winner is not None:
        st.write(f"Player {st.session_state.winner} wins!")
        if st.button("New Game"):
            reset_game()
    else:
        draw_grid(st.session_state.game.board)

if __name__ == '__main__':
    main()
