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
        self.x, self.y = 145 + self.position * 180, 580
        self.length, self.height = 70, 30
        self.state = False

    def activate(self):
        self.state = not self.state

    def cursor_is_in(self, mouse_position):
        return self.x <= mouse_position[0] <= self.x + self.length and self.y <= mouse_position[
            1] <= self.y + self.height

    def draw(self, screen_in):
        pygame.draw.rect(screen_in, self.colors[self.state], (self.x, self.y, self.length, self.height))


class Disc:
    def __init__(self, size: int):
        self.moving_speed = 20
        self.size = size
        self.length, self.height = 50 + 23 * self.size, 30
        self.x, self.y = 180 - self.length // 2, 385 + 30*(size - 1)
        self.destination = None
        self.arrived_on_top = False  # set on True if disc arrives at the top during movement to the other peg
        self.arrived_on_peg = False  # set on True if disc arrives at top of the destination peg
        self.arrived_on_bottom = False  # set on True if disc has arrived at destination during movement

    def move(self):
        if not self.arrived_on_top:  # move up until reaching the top limit of the movement of the disk
            self.y -= self.moving_speed
            if self.y <= 120:
                self.y, self.arrived_on_top = 120, True
        elif not self.arrived_on_peg:  # move horizontally until reaching the destination peg
            self.x += self.moving_speed
            if self.x >= self.destination[0]:
                self.x, self.arrived_on_peg = self.destination[0], True
        else:  # move down until reaching destination
            self.y += self.moving_speed
            if self.y >= self.destination[1]:
                self.y, self.arrived_on_bottom = self.destination[1], True
                self.destination = None

    def set_destination(self, peg_index, order_on_peg):
        self.destination = (180*(1+peg_index) - self.length // 2, 565 - order_on_peg * 30)

    def draw(self, screen_in):
        pygame.draw.rect(screen_in, (100, 50, 0), (self.x, self.y, self.length, self.height))
        pygame.draw.rect(screen_in, (0, 0, 0), (self.x, self.y, self.length, self.height), 2)


class Board:
    def __init__(self, d_n):
        self.pegs: [[Disc], [Disc], [Disc]] = [[], [], []]
        self.disc_number = d_n
        self.origin_peg = None
        self.destination_peg = None
        self.disc_is_moving = False
        self.create_board()

    def create_board(self):
        self.pegs[0] = [Disc(size) for size in list(range(1, self.disc_number+1))]

    def create_moving_disc(self, origin_peg_index: int, destination_peg_index: int):
        self.origin_peg, self.destination_peg = origin_peg_index, destination_peg_index
        self.pegs[origin_peg_index][0].set_destination(self.destination_peg, len(self.pegs[self.destination_peg])+1)
        self.disc_is_moving = True

    def draw(self, screen_in):
        drawing_pegs = self.pegs[::]  # do not delete
        for peg in drawing_pegs:
            for disc in peg:
                if disc.destination:
                    disc.move()
                    if disc.arrived_on_bottom:
                        disc.destination = None
                        disc.arrived_on_bottom, disc.arrived_on_peg, disc.arrived_on_top = False, False, False
                        self.pegs[self.origin_peg].pop(0)
                        self.pegs[self.destination_peg].insert(0, disc)
                        self.disc_is_moving = False
                disc.draw(screen_in)

    def __str__(self):
        string = ""
        for i in range(3):
            string += f"Peg {i+1}: "+" ".join([str(disc.size) for disc in self.pegs[i]])+"\n"
        return string


class Tower_of_Hanoi:
    def __init__(self, screen_in, d_number: int):
        self.screen = screen_in
        self.board = Board(d_number % 7)  # more than 7 discs is not allowed
        self.moves_number = 0
        self.image = pygame.image.load("setup.png").convert_alpha()
        self.actions = []
        self.buttons = [Button(i) for i in range(3)]
        self.draw_rect = pygame.draw.rect

    def action_is_allowed(self) -> bool:
        orig_peg = self.board.pegs[self.actions[0]]  # origin peg
        des_peg = self.board.pegs[self.actions[1]]  # destination pegs
        # origin peg is not empty and destination peg is either empty or top-peg is smaller than incoming peg
        if orig_peg and (not des_peg or orig_peg[0].size < des_peg[0].size):
            self.moves_number += 1  # if action is allowed, the number of moves is incremented
            return True

    def get_mouse_position(self, peg: [])-> (int, int):
        if peg is self.board.pegs[0]:
            return 150, 590
        if peg is self.board.pegs[1]:
            return 330, 590
        if peg is self.board.pegs[2]:
            return 510, 590

    def get_moves(self, d_number, source, target, bridge, moves):
        if d_number <= 0:
            return None
        # move n - 1 disks from source to bridge, so they are out of the way
        self.get_moves(d_number - 1, source, bridge, target, moves)
        # move the nth disk from source to target
        moves.append((self.get_mouse_position(source), self.get_mouse_position(target)))
        # Display our progress
        # move the n - 1 disks that we left on bridge onto target
        self.get_moves(d_number - 1, bridge, target, source, moves)
        return moves

    def auto_solve(self):
        moves = self.get_moves(self.board.disc_number, self.board.pegs[0],  self.board.pegs[2], self.board.pegs[1], [])
        self.__init__(self.screen, self.board.disc_number)  # reset the board since previous step messed it
        current_move = 0
        while current_move <= len(moves):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()
            if not self.board.disc_is_moving:
                self.activate_button(moves[current_move][0])
                self.activate_button(moves[current_move][1])
                current_move += 1
            self.refresh()
            CLOCK.tick(FPS)
        pygame.time.wait(10000)  # prevent window from closing

    def human_solve(self):
        while not self.goal_test():
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()
                elif not self.goal_test() and event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed(3)[0]:
                    self.activate_button(pygame.mouse.get_pos())
            self.refresh()
            CLOCK.tick(FPS)
        self.refresh()
        pygame.time.wait(5000)

    def move_disc(self) -> None:
        if self.action_is_allowed():
            self.board.create_moving_disc(self.actions[0], self.actions[1])

    def goal_test(self) -> bool:
        return not (self.board.pegs[0] or self.board.pegs[1])

    def draw(self) -> None:
        self.screen.blit(self.image, (0, 0))
        self.board.draw(self.screen)
        self.screen.blit(FONT.render(str(self.moves_number), True, (153, 217, 234)), (145, 24))
        [button.draw(self.screen) for button in self.buttons]
        if len(self.actions) == 2:  # must be here to maintain buttons active until disc reaches destination
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

    def refresh(self):
        self.draw()
        if self.goal_test():
            self.screen.blit(pygame.image.load("winner.png").convert_alpha(), (0, 0))
        pygame.display.update()


if __name__ == "__main__":
    game_mode = ""
    while game_mode != "1" and game_mode != "2":
        game_mode = input("What mode you want to play? \n  1- AI\n  2- Human \ninput: ")
    disc_number = 0
    while disc_number < 2 or disc_number > 7:
        disc_number = int(input("Enter the number of discs: "))
    Game = Tower_of_Hanoi(screen, disc_number)
    if game_mode == "1":
        Game.auto_solve()
    elif game_mode == "2":
        Game.human_solve()
