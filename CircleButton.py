import pygame


class CircleButton:
    def __init__(self, pos, text_input, font, base_color, hovering_color, radius):
        self.x_pos = pos[0]
        self.y_pos = pos[1]
        self.font = font
        self.base_color, self.hovering_color = base_color, hovering_color
        self.text_input = text_input
        self.text = self.font.render(self.text_input, True, self.base_color)
        self.rect = self.text.get_rect(center=(self.x_pos, self.y_pos))
        self.radius = radius

    def update(self, screen):
        pygame.draw.circle(screen, self.base_color, (self.x_pos, self.y_pos), self.radius)
        screen.blit(self.text, self.rect)

    def checkForInput(self, position):
        distance = ((position[0] - self.x_pos) ** 2 + (position[1] - self.y_pos) ** 2) ** 0.5
        if distance <= self.radius:
            return True
        return False

    def changeColor(self, position):
        distance = ((position[0] - self.x_pos) ** 2 + (position[1] - self.y_pos) ** 2) ** 0.5
        if distance <= self.radius:
            self.text = self.font.render(self.text_input, True, self.hovering_color)
        else:
            self.text = self.font.render(self.text_input, True, self.base_color)
