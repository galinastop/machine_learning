import pygame
import numpy as np

colors = [
    "#000000", "#BA0900", "#6B7900", "#00C2A0", "#FFAA92", "#FF90C9", "#B903AA", "#D16100",
    "#DDEFFF", "#000035", "#7B4F4B", "#A1C299", "#300018", "#0AA6D8", "#013349", "#00846F",
    "#372101", "#FFB500", "#C2FFED", "#A079BF", "#CC0744", "#C0B9B2", "#C2FF99", "#001E09",
    "#00489C", "#6F0062", "#0CBD66", "#EEC3FF", "#456D75", "#B77B68", "#7A87A1", "#788D66",
    "#885578", "#FAD09F", "#FF8A9A", "#D157A0", "#BEC459", "#456648", "#0086ED", "#886F4C"
]


def dist(pnt1, pnt2):
    return np.sqrt((pnt1[0] - pnt2[0]) ** 2 + (pnt1[1] - pnt2[1]) ** 2)


def dbscan(points, eps):
    minPts = 3

    # fill red
    flag = ['r' for _ in range(len(points))]

    # green
    for i, pnt1 in enumerate(points):
        number_pts = 0

        for pnt2 in points:
            if pnt1 != pnt2 and dist(pnt1, pnt2) < eps:
                number_pts += 1

        if number_pts >= minPts:
            flag[i] = 'g'

    # yellow
    for i, pnt1 in enumerate(points):
        if flag[i] != 'g':
            for j, pnt2 in enumerate(points):
                if flag[j] == 'g' and pnt1 != pnt2 and dist(pnt1, pnt2) < eps:
                    flag[i] = 'y'
                    break

    # grouping
    groups = [0 for _ in range(len(points))]

    g = 0
    for i, pnt1 in enumerate(points):
        if flag[i] == 'g' and groups[i] == 0:
            g += 1
            dfs(pnt1, points, groups, flag, eps, g)

    return flag, groups

def is_closest(pnt1, pnt2, points, flags, eps):
    closest = dist(pnt2, pnt1)
    for i, pnt3 in enumerate(points):
        if flags[i] == 'g' and dist(pnt2, pnt3) < eps and dist(pnt2, pnt3) < closest:
            return False
    return True


def dfs(pnt1, points, groups, flags, eps, g):
    for i, pnt2 in enumerate(points):
        if groups[i] == 0 and dist(pnt1, pnt2) < eps:
            if flags[i] == 'g':
                groups[i] = g
                dfs(pnt2, points, groups, flags, eps, g)
            elif flags[i] == 'y':
                if is_closest(pnt1, pnt2, points, flags, eps):
                    groups[i] = g


def colorize_groups(points, groups, screen):
    screen.fill('white')

    for i, pnt in enumerate(points):
        pygame.draw.circle(screen, color=colors[groups[i]], center=pnt, radius=10)

    pygame.display.update()


def start():
    pygame.init()

    screen = pygame.display.set_mode((800, 600))
    running = True
    radius_mode = False
    green_mode = False
    yellow_mode = False
    red_mode = False
    eps = 60

    screen.fill("white")

    pygame.display.update()
    points = paint(screen, eps)

    flags, groups = dbscan(points, eps)

    screen.fill("white")
    colorize(points, flags, screen, lambda f: True, 'black')

    while running:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    colorize(points, flags, screen, lambda f: f == 'g', 'green')
                    green_mode = True
                if event.key == pygame.K_2:
                    colorize(points, flags, screen, lambda f: f == 'y', 'yellow')
                    yellow_mode = True
                if event.key == pygame.K_3:
                    colorize(points, flags, screen, lambda f: f == 'r', 'red')
                    red_mode = True
                if event.key == pygame.K_4:
                    colorize(points, flags, screen, lambda f: True, 'black')
                    green_mode, yellow_mode, red_mode = False, False, False
                if event.key == pygame.K_5:
                    radius_mode = not radius_mode
                    radius(radius_mode, eps, points, screen, (green_mode, yellow_mode, red_mode, flags))
                if event.key == pygame.K_6:
                    if radius_mode:
                        radius_mode = False
                        radius(radius_mode, eps, points, screen, (green_mode, yellow_mode, red_mode, flags))
                    exit = iterate(points, flags, screen, eps)
                    if exit:
                        running = False
                if event.key == pygame.K_7:
                    colorize_groups(points, groups, screen)
            if event.type == pygame.QUIT:
                running = False


def iterate(points, flags, screen, eps):
    iterating = True
    exit = False

    def i_draw(i):
        screen.fill('white')
        colorize(points, flags, screen, lambda f: True, 'black', False)
        pnt1 = points[i]
        if flags[i] == 'y':
            colorize([pnt1], flags, screen, lambda f: True, 'yellow', False)
            for j, pnt2 in enumerate(points):
                if flags[j] == 'g' and pnt1 != pnt2 and dist(pnt1, pnt2) < eps:
                    colorize([pnt2], flags, screen, lambda f: True, 'green', False)

        else:
            if flags[i] == 'r':
                colorize([pnt1], flags, screen, lambda f: True, 'red', False)
            else:
                colorize([pnt1], flags, screen, lambda f: True, 'green', False)

        radius(True, eps, [pnt1], screen, (False, False, False, flags), False)
        pygame.display.update()

    i = 0
    i_draw(i)
    while iterating:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    i += 1
                    if i > len(points) - 1:
                        i = 0
                    i_draw(i)
                if event.key == pygame.K_LEFT:
                    i -= 1
                    if i < 0:
                        i = len(points) - 1
                    i_draw(i)
                if event.key == pygame.K_6:
                    screen.fill('white')
                    colorize(points, flags, screen, lambda f: True, 'black')
                    iterating = False
            if event.type == pygame.QUIT:
                iterating = False
                exit = True

    return exit


def radius(toggle, eps, points, screen, color_modes, update=True):
    if (toggle):
        for pnt in points:
            radius_surface = pygame.Surface((2 * eps, 2 * eps), pygame.SRCALPHA)
            pygame.draw.circle(radius_surface, color=(0, 0, 0, 10), center=(eps, eps), radius=eps)
            screen.blit(radius_surface, (pnt[0] - eps, pnt[1] - eps))
    else:
        flags = color_modes[-1]
        screen.fill('white')
        colorize(points, flags, screen, lambda f: True, 'black')
        if color_modes[0]:
            colorize(points, flags, screen, lambda f: f == 'g', 'green')
        if color_modes[1]:
            colorize(points, flags, screen, lambda f: f == 'y', 'yellow')
        if color_modes[2]:
            colorize(points, flags, screen, lambda f: f == 'r', 'red')

    if update:
        pygame.display.update()


def colorize(points, flags, screen, condition, color, update=True):
    for i, pnt in enumerate(points):
        if condition(flags[i]):
            pygame.draw.circle(screen, color=color, center=pnt, radius=10)
    if update:
        pygame.display.update()


def follow_mouse(pos, points, screen, eps):
    screen.fill('white')
    colorize(points, points, screen, lambda f: True, 'black')
    colorize([pos], ['b'], screen, lambda f: True, 'black')
    radius(True, eps, [pos], screen, (False, False, False, []))


def paint(screen, eps):
    points = []

    painting = True
    while painting:
        for event in pygame.event.get():
            follow_mouse(pygame.mouse.get_pos(), points, screen, eps)

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    points.append(event.pos)
                    pygame.draw.circle(screen, color='black', center=event.pos, radius=10)
                    pygame.display.update()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return points

            if event.type == pygame.QUIT:
                painting = False


if __name__ == '__main__':
    start()
