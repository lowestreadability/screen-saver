from math import sqrt
from random import random
import pygame


class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y)

    def __mul__(self, k):
        return Vector(self.x * k, self.y * k)

    def __len__(self):
        return sqrt(self.x * self.x + self.y * self.y)

    def __str__(self):
        return '({}, {})'.format(self.x, self.y)

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def int_pair(self):
        return int(self.x), int(self.y)


class Line:
    def __init__(self, screen_size, game_display):
        self.screen_size = screen_size
        self.game_display = game_display

    def get_point(self, points, alpha, deg=None):
        if deg is None:
            deg = len(points) - 1
        if deg == 0:
            return points[0]
        vector1 = Vector(points[deg].get_x(), points[deg].get_y())
        vector2 = Vector(self.get_point(points, alpha, deg - 1).get_x(),
                         self.get_point(points, alpha, deg - 1).get_y())
        return vector1 * alpha + vector2 * (1 - alpha)

    def get_points(self, base_points, count):
        alpha = 1 / count
        result = []
        for i in range(count):
            result.append(self.get_point(base_points, i * alpha))
        return result

    def set_points(self, points, speeds):
        for point in range(len(points)):
            vec1 = Vector(points[point].get_x(),
                          points[point].get_y())
            vec2 = Vector(speeds[point].get_x(),
                          speeds[point].get_y())
            points[point] = vec1 + vec2
            if points[point].get_x() > self.screen_size[0] or points[point].get_x() < 0:
                speeds[point] = Vector(- speeds[point].get_x(), speeds[point].get_y())
            if points[point].get_y() > self.screen_size[1] or points[point].get_y() < 0:
                speeds[point] = Vector(speeds[point].get_x(), -speeds[point].get_y())

    def draw_points(self, points, style="points", width=4, color=(255, 255, 255)):
        if style == "line":
            for point_number in range(-1, len(points) - 1):
                pygame.draw.line(self.game_display, color, points[point_number].int_pair(),
                                 points[point_number + 1].int_pair(), width)

        elif style == "points":
            for point in points:
                pygame.draw.circle(self.game_display, color,
                                   point.int_pair(), width)


class Joint(Line):
    def __init__(self, screen_size, game_display):
        super().__init__(screen_size, game_display)

    def get_joint(self, points, count):
        if len(points) < 3:
            return []
        result = []
        for i in range(-2, len(points) - 2):
            pnt = []

            vec1 = Vector(points[i].get_x(), points[i].get_y())
            vec2 = Vector(points[i + 1].get_x(), points[i + 1].get_y())
            vec3 = Vector(points[i + 2].get_x(), points[i + 2].get_y())

            pnt.append((vec1+vec2)*0.5)
            pnt.append(vec2)
            pnt.append((vec2+vec3)*0.5)

            result.extend(self.get_points(pnt, count))
        return result


class Game:
    def __init__(self, caption, width, height):
        self.screen_size = (width, height)
        self.width = width
        self.height = height
        pygame.init()
        self.game_display = pygame.display.set_mode(self.screen_size)
        pygame.display.set_caption(caption)

        self.steps = 0
        self.working = True
        self.points = []
        self.speeds = []
        self.show_help = False
        self.pause = False
        self.speed = 20

        self.color_param = 0
        self.color = pygame.Color(0)

    def display_help(self):
        self.game_display.fill((50, 50, 50))
        font1 = pygame.font.SysFont("arial", 30)
        font2 = pygame.font.SysFont("serif", 30)

        data = []
        data.append(["F1", "Помощь"])
        data.append(["R", "Перезапуск"])
        data.append(["P", "Воспроизвести / Пауза"])
        data.append(["9", "Добавить точку"])
        data.append(["0", "Удалить точку"])
        data.append(["", ""])
        data.append([str(self.steps), "текущих точек"])

        pygame.draw.lines(self.game_display, (255, 50, 50, 255), True, [
            (0, 0), (800, 0), (800, 600), (0, 600)], 5)
        for item, text in enumerate(data):
            self.game_display.blit(font1.render(
                text[0], True, (128, 128, 255)), (100, 100 + 30 * item))
            self.game_display.blit(font2.render(
                text[1], True, (128, 128, 255)), (200, 100 + 30 * item))

    def run(self):
        while self.working:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.working = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.working = False
                    if event.key == pygame.K_r:
                        self.points = []
                        self.speeds = []
                    if event.key == pygame.K_p:
                        self.pause = not self.pause
                    if event.key == pygame.K_KP_PLUS:
                        self.steps += 1
                    if event.key == pygame.K_F1:
                        self.show_help = not self.show_help
                    if event.key == pygame.K_KP_MINUS:
                        self.steps -= 1 if self.steps > 1 else 0
                    if event.key == pygame.K_2:
                        self.speed *= 1.3
                        for i in range(len(self.speeds)):
                            self.speeds[i] *= 1.3
                    if event.key == pygame.K_1:
                        self.speed *= 0.8
                        for i in range(len(self.speeds)):
                            self.speeds[i] *= 0.8
                    if event.key == pygame.K_0:
                        self.points.pop(0)
                        self.speeds.pop(0)
                        self.steps -= 1
                    if event.key == pygame.K_9:
                        self.points.append(Vector(self.width//2, self.height//2))
                        self.speeds.append(Vector(random() * self.speed, random() * self.speed))
                        self.steps += 1

                if event.type == pygame.MOUSEBUTTONUP:
                    self.points.append(Vector(event.pos[0], event.pos[1]))
                    self.speeds.append(Vector(random() * self.speed, random() * self.speed))
                    self.steps += 1

            self.game_display.fill((0, 0, 0))
            self.color_param = (self.color_param + 1) % 360
            self.color.hsla = (self.color_param, 100, 50, 100)

            line = Line(self.screen_size, self.game_display)
            line.draw_points(self.points)
            joint = Joint(self.screen_size, self.game_display)
            line.draw_points(joint.get_joint(self.points, self.steps), "line", 4, self.color)
            if not self.pause:
                line.set_points(self.points, self.speeds)
            if self.show_help:
                self.display_help()

            pygame.display.flip()

        pygame.display.quit()
        pygame.quit()
        exit(0)


def main():
    game = Game('Screen saver', 1280, 720)
    game.run()


if __name__ == '__main__':
    main()