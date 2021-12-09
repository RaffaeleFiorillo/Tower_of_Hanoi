import pygame
pygame.init()

WIDTH, HEIGHT = 720, 650
FPS = 60
FONT = pygame.font.SysFont("Times New Roman", 36, True)
CLOCK = pygame.time.Clock()
DISC_NUMBER = 6
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hanoi Tower")


class Button:
    colors = {True: (0, 255, 255), False: (0, 0, 255)}

    def __init__(self, position):
        self.position = position
        self.x, self.y = 145+self.position*180, 580
        self.length, self.height = 70, 30
        self.state = False

    def activate(self):
        self.state = not self.state

    def cursor_is_in(self, mouse_position):
        return self.x <= mouse_position[0] <= self.x+self.length and self.y <= mouse_position[1] <= self.y+self.height

    def draw(self, screen_in):
        pygame.draw.rect(screen_in, self.colors[self.state], (self.x, self.y, self.length, self.height))


class Board:
    def __init__(self, disc_number: int):
        self.total_discs = disc_number % 7
        self.board = [[i+1 for i in range(disc_number)], [], []]
        self.moves_number = 0
        self.image = pygame.image.load("setup.png").convert_alpha()
        self.actions = []
        self.buttons = [Button(i) for i in range(3)]
        self.draw_rect = pygame.draw.rect

    def action_is_allowed(self) -> bool:
        orig_peg, des_peg = self.board[self.actions[0]], self.board[self.actions[1]]  # origin and destination pegs
        if orig_peg and (not des_peg or orig_peg[0] < des_peg[0]):
            return True

    def move_disc(self) -> None:
        if self.action_is_allowed():
            self.board[self.actions[1]].insert(0, self.board[self.actions[0]].pop(0))  # move disc to destination
            self.moves_number += 1

    def goal_test(self) -> bool:
        return not (self.board[0] or self.board[1])

    def get_rect(self, peg_number: int, disc_number: int, disc_size: int) -> (int, int, int, int):
        length, height = 60+26*(disc_size-1), 30
        x, y = 180+180*peg_number-length//2, 563-(disc_number+1)*30
        return x, y, length, height

    def draw_discs(self, screen_in):
        for peg_num, peg in enumerate(self.board):
            for disc_num, disc_size in enumerate(peg[::-1]):
                self.draw_rect(screen_in, (100, 50, 0), self.get_rect(peg_num, disc_num, disc_size))
                self.draw_rect(screen_in, (0, 0, 0), self.get_rect(peg_num, disc_num, disc_size), 2)

    def draw(self, screen_in: pygame.Surface) -> None:
        screen_in.blit(self.image, (0, 0))
        self.draw_discs(screen_in)
        screen_in.blit(FONT.render(str(self.moves_number), True, (153, 217, 234)), (145, 24))
        [button.draw(screen_in) for button in self.buttons]
        if len(self.actions) == 2:
            self.move_disc()
            self.buttons[self.actions[0]].activate()
            self.buttons[self.actions[1]].activate()
            self.actions = []

    def activate_button(self, mouse_position: (int, int)) -> None:
        for button in self.buttons:
            if button.cursor_is_in(mouse_position):
                button.activate()
                if not self.actions or self.actions[0] != button.position:
                    self.actions.append(button.position)
                else:
                    self.actions = []
                break


def refresh(screen_in, board_in, last=False):
    board_in.draw(screen_in)
    if last:
        screen.blit(pygame.image.load("winner.png").convert_alpha(), (0, 0))
    pygame.display.update()


def main(game_over=False):
    board = Board(DISC_NUMBER)
    while not board.goal_test():
        CLOCK.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            elif not game_over and event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed(3)[0]:
                board.activate_button(pygame.mouse.get_pos())
        refresh(screen, board, game_over)
    main(True)


main()
