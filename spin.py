# A Pygame-based interactive Giveaway Wheel of Fortune that lets users input participants and games, then spins a colorful wheel to randomly select and display winners with smooth animation and clipboard support.

import pygame
import random
import sys
import math
import pyperclip  # Import the pyperclip module

pygame.init()
WIDTH, HEIGHT = 1000, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("🎡 Giveaway Wheel of Fortune")

FONT = pygame.font.SysFont("Arial", 24)
BIG_FONT = pygame.font.SysFont("Arial", 48, bold=True)
clock = pygame.time.Clock()

class InputBox:
    def __init__(self, x, y, w, h, prompt):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = ''
        self.prompt = prompt
        self.active = False
        self.cursor_visible = True
        self.cursor_timer = 0
        self.is_focused = False  # Track focus

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
            self.is_focused = self.active

        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                return 'submit'
            elif event.key == pygame.K_TAB:
                return 'tab'
            else:
                self.text += event.unicode

            # Allow pasting with Ctrl+V
            if event.key == pygame.K_v and pygame.key.get_pressed()[pygame.K_LCTRL]:
                clipboard_content = pyperclip.paste()  # Get text from clipboard
                self.text += self.sanitize_clipboard_content(clipboard_content)  # Sanitize and add text

    def update(self):
        self.cursor_timer += 1
        if self.cursor_timer >= 30:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0

    def draw(self, surface):
        # Set the border color to bright green if active
        border_color = pygame.Color('green') if self.active else pygame.Color('white')
        pygame.draw.rect(surface, border_color, self.rect, 2)
        prompt_surface = FONT.render(self.prompt, True, pygame.Color("gray"))
        surface.blit(prompt_surface, (self.rect.x, self.rect.y - 30))

        text_surface = FONT.render(self.text, True, pygame.Color("white"))
        surface.blit(text_surface, (self.rect.x + 5, self.rect.y + 10))

        if self.active and self.cursor_visible:
            cursor_x = self.rect.x + 5 + text_surface.get_width()
            cursor_y = self.rect.y + 10
            pygame.draw.line(surface, pygame.Color("white"), (cursor_x, cursor_y), (cursor_x, cursor_y + text_surface.get_height()), 2)

    def get_text(self):
        return self.text.strip()

    def clear(self):
        self.text = ''

    def sanitize_clipboard_content(self, content):
        """Sanitize clipboard content to prevent invalid characters"""
        # Only keep printable characters from clipboard content
        return ''.join(c for c in content if c.isprintable())

class Button:
    def __init__(self, rect, text, color=(70,130,180), text_color=(255,255,255)):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.color = color
        self.text_color = text_color

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect, border_radius=8)
        txt_surf = FONT.render(self.text, True, self.text_color)
        surface.blit(txt_surf, txt_surf.get_rect(center=self.rect.center))

    def is_clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos)

def input_screen():
    name_box = InputBox(50, 100, 400, 50, "Enter Participant Name")
    game_box = InputBox(50, 200, 400, 50, "Enter Game Title")
    start_button = Button((50, 300, 550, 50), "Start Giveaway", color=(34,139,34))

    participants, games = [], []
    input_boxes = [name_box, game_box]
    current_box = 0  # Start with the first input box

    while True:
        screen.fill((25, 25, 35))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            # Handle events for the current input box
            result_name = name_box.handle_event(event)
            result_game = game_box.handle_event(event)

            if result_name == 'submit':
                name = name_box.get_text()
                if name: participants.append(name)
                name_box.clear()

            if result_game == 'submit':
                game = game_box.get_text()
                if game: games.append(game)
                game_box.clear()

            if result_name == 'tab':
                current_box = (current_box + 1) % len(input_boxes)
                name_box.active = False
                game_box.active = False
                input_boxes[current_box].active = True

            if result_game == 'tab':
                current_box = (current_box + 1) % len(input_boxes)
                name_box.active = False
                game_box.active = False
                input_boxes[current_box].active = True

            if start_button.is_clicked(event):
                if participants and games:
                    return participants, games

        name_box.update()
        game_box.update()

        name_box.draw(screen)
        game_box.draw(screen)
        start_button.draw(screen)

        screen.blit(FONT.render("Participants:", True, pygame.Color("lightgreen")), (650, 50))
        for i, p in enumerate(participants[-12:]):
            screen.blit(FONT.render(p, True, pygame.Color("white")), (650, 80 + i * 28))

        screen.blit(FONT.render("Games:", True, pygame.Color("gold")), (650, 440))
        for i, g in enumerate(games[-12:]):
            screen.blit(FONT.render(g, True, pygame.Color("white")), (650, 470 + i * 28))

        pygame.display.flip()
        clock.tick(30)

def draw_wheel(screen, items, angle_offset):
    center = (WIDTH // 2, HEIGHT // 2)
    radius = 300
    total = len(items)
    for i, item in enumerate(items):
        angle = 2 * math.pi * i / total + angle_offset
        x = center[0] + radius * math.cos(angle)
        y = center[1] + radius * math.sin(angle)
        pygame.draw.line(screen, pygame.Color("white"), center, (x, y), 2)

        label_angle = angle + (math.pi / total)
        lx = center[0] + (radius - 60) * math.cos(label_angle)
        ly = center[1] + (radius - 60) * math.sin(label_angle)
        label = FONT.render(item, True, pygame.Color("cyan"))
        rect = label.get_rect(center=(lx, ly))
        screen.blit(label, rect)

    pygame.draw.circle(screen, pygame.Color("white"), center, 10)

def spin_wheel(items, winner_text):
    angle = 0
    velocity = random.uniform(0.5, 1.5)
    friction = 0.98
    selected_index = None
    spinning = True

    while spinning:
        screen.fill((0, 0, 0))
        draw_wheel(screen, items, angle)
        pygame.display.flip()
        angle += velocity
        velocity *= friction
        clock.tick(60)

        if velocity < 0.002:
            spinning = False
            selected_index = int((angle % (2 * math.pi)) / (2 * math.pi / len(items)))
            selected_index = len(items) - 1 - selected_index
            selected_index %= len(items)

    winner = items[selected_index]
    winner_message = f"{winner_text}: {winner}"
    for _ in range(120):
        screen.fill((0, 0, 0))
        draw_wheel(screen, items, angle)
        label = BIG_FONT.render(winner_message, True, pygame.Color("yellow"))
        screen.blit(label, label.get_rect(center=(WIDTH//2, 50)))
        pygame.display.flip()
        clock.tick(60)

def main_game():
    participants, games = input_screen()

    while True:
        screen.fill((0, 0, 0))
        spin_wheel(participants, "Winner")
        pygame.time.delay(1000)
        spin_wheel(games, "Game")
        pygame.time.delay(2000)

        cont_button = Button((WIDTH//2 - 100, HEIGHT - 100, 200, 50), "Spin Again")
        quit_button = Button((WIDTH//2 - 100, HEIGHT - 40, 200, 50), "Quit", color=(178,34,34))

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if cont_button.is_clicked(event):
                    break
                if quit_button.is_clicked(event):
                    pygame.quit(); sys.exit()

            cont_button.draw(screen)
            quit_button.draw(screen)
            pygame.display.flip()
            clock.tick(30)
            if cont_button.is_clicked(event):
                break

if __name__ == "__main__":
    main_game()
