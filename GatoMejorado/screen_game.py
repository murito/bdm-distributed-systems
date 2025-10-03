import pygame

from load_sprite import LoadSprite
from p2p_node import broadcast_message, get_bit

class ScreenGame:
    def __init__(self, screen, gato):
        print("Initializing ScreenGame")
        self.board = None
        self.screen = screen
        self.gato = gato
        self.grid = []
        self.color = (200, 200, 200)
        self.x_sprite = None
        self.o_sprite = None
        self.moves_grid_bits = [
            [8  ,16  ,  32],
            [64 ,128 , 256],
            [512,1024,2048]
        ]

    def who_win(self):
        sum_cols = []
        for col in range(3):
            c1 = 1 if self.gato.game_state[0][col] == self.gato.player else 0
            c2 = 1 if self.gato.game_state[1][col] == self.gato.player else 0
            c3 = 1 if self.gato.game_state[2][col] == self.gato.player else 0
            sum_cols.append(c1 + c2 + c3)

        sum_rows = []
        for row in range(3):
            r1 = 1 if self.gato.game_state[row][0] == self.gato.player else 0
            r2 = 1 if self.gato.game_state[row][1] == self.gato.player else 0
            r3 = 1 if self.gato.game_state[row][2] == self.gato.player else 0
            sum_rows.append(r1 + r2 + r3)

        diagonal1 = [1 if self.gato.game_state[0][0] == self.gato.player else 0,
                     1 if self.gato.game_state[1][1] == self.gato.player else 0,
                     1 if self.gato.game_state[2][2] == self.gato.player else 0]

        diagonal2 = [1 if self.gato.game_state[0][2] == self.gato.player else 0,
                     1 if self.gato.game_state[1][1] == self.gato.player else 0,
                     1 if self.gato.game_state[2][0] == self.gato.player else 0]

        # 8 chances to win
        if (
            sum_cols[0] == 3 or
            sum_cols[1] == 3 or
            sum_cols[2] == 3 or
            sum_rows[0] == 3 or
            sum_rows[1] == 3 or
            sum_rows[2] == 3 or
            sum(diagonal1) == 3 or
            sum(diagonal2) == 3
        ):
            winner_bits = 4096 if self.gato.player == 1 else 8192
            self.gato.winner = self.gato.player
            self.gato.game_state_bits = self.gato.game_state_bits | winner_bits  # activate bit 12 P1 or 13 P2

        # Draw
        empty_cells = 9
        for row in self.gato.game_state:
            for cell in row:
                if cell != 0:
                    empty_cells -= 1

        if empty_cells == 1 and self.gato.winner == 0:
            self.gato.winner = 3  # Draw
            self.gato.game_state_bits = self.gato.game_state_bits | 16384  # activate bit 14
            print("Draw ")

        # TODO: remove debug print
        print(self.gato.game_state)

        self.gato.clock.tick(30)

    def on_init(self):
        self.board = pygame.image.load("images/board.png").convert_alpha()

        self.x_sprite = LoadSprite((0, 0), 93, 83, pygame.image.load("images/XO.png").convert_alpha())
        self.o_sprite = LoadSprite((93,0),88, 83, pygame.image.load("images/XO.png").convert_alpha())

        # build the clickable grid
        w,h = 92,92
        self.grid = [
            [pygame.Rect(102, 129, w, h),pygame.Rect(214, 129, w, h),pygame.Rect(327, 129, w, h)],
            [pygame.Rect(102, 239, w, h), pygame.Rect(214, 239, w, h), pygame.Rect(327, 239, w, h)],
            [pygame.Rect(102, 350, w, h), pygame.Rect(214, 350, w, h), pygame.Rect(327, 350, w, h)]
        ]

    def on_event(self, event):
        grid_row = 0
        # intercept cliks on each frame of the grid
        if event.type == pygame.MOUSEBUTTONDOWN:
            for row in self.grid:
                grid_col = 0
                for rct in row:
                    # you must be in game screen to make a move
                    # you must be on your turn
                    # The position you hit must not be occupied
                    if rct.collidepoint(event.pos) and self.gato.CURRENT_SCREEN == 3 and self.gato.turn and self.gato.game_state[grid_row][grid_col] == 0:
                        # mark move graphic
                        self.gato.game_state[grid_row][grid_col] = 1 if self.gato.player == 1 else 2

                        # Determine the winner
                        self.who_win()

                        # pass the turn
                        self.gato.turn = False

                        # switch turns on bit state
                        if self.gato.player == 1:
                            self.gato.game_state_bits = self.gato.game_state_bits | 4 #turn on bit 2

                        if self.gato.player == 2:
                            self.gato.game_state_bits = self.gato.game_state_bits & ~4 # turn off bit 2

                        # add your move
                        self.gato.game_state_bits = self.gato.game_state_bits | self.moves_grid_bits[grid_row][grid_col]

                        # identify who made the move
                        if self.gato.player == 1:
                            self.gato.game_state_bits = self.gato.game_state_bits & ~2 #turn on bit 1

                        if self.gato.player == 2:
                            self.gato.game_state_bits = self.gato.game_state_bits | 2 #turn off bit 1
                        
                        # send actions
                        broadcast_message(str(self.gato.game_state_bits))
                    grid_col += 1
                grid_row += 1
        pass

    def on_render(self):
        self.screen.blit(self.board, (0, 0))

        # update turn label
        if self.gato.winner == 0:
            self.gato.label_turn.update("Turno: Tu turno!" if self.gato.turn else "Turno: Esperando judador...")

        if not self.gato.turn:
            self.screen.blit(self.gato.waiting_bg, (0, 0))

        # print grid
        for row in self.grid:
            for rct in row:
                pygame.draw.rect(self.screen, self.color, rct, 2)

        # print moves
        grid_row = 0
        for row in self.gato.game_state:
            grid_col = 0
            for col in row:
                rct = self.grid[grid_row][grid_col]
                if self.gato.game_state[grid_row][grid_col] == 1:
                    self.screen.blit(self.x_sprite.cropped, (rct.x - 4, rct.y + 4))

                if self.gato.game_state[grid_row][grid_col] == 2:
                    self.screen.blit(self.o_sprite.cropped, (rct.x, rct.y + 4))

                grid_col += 1
            grid_row += 1