# Example file showing a circle moving on screen
import pygame

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
dt = 0

player_pos = pygame.Vector2(screen.get_width() / 2 - 40, screen.get_height() - 40)
player_size = pygame.Vector2(80, 30)
cube_center = pygame.Vector2(player_pos.x + 40, player_pos.y + 15)
ball_pos = pygame.Vector2(screen.get_width() / 2, screen.get_height() - 50)
ball_velocity = pygame.Vector2(0, 0)
has_started = False

def getLineIntersection(p0: pygame.Vector2, p1: pygame.Vector2, p2: pygame.Vector2, p3: pygame.Vector2):
    vec = pygame.Vector2(0,0)
    s1 = p1 - p0
    s2 = p3 - p2

    denom = (-s2.x * s1.y + s1.x * s2.y)
    if denom == 0:
        print("denom is 0")
        return (False, vec)

    s = (-s1.y * (p0.x - p2.x) + s1.x * (p0.y - p2.y)) / denom 
    t = (s2.x * (p0.y - p2.y) - s2.y * (p0.x - p2.x)) / denom

    if s >= 0 and s <= 1 and t >= 0 and t <= 1:
        vec.x = p0.x + (t * s1.x)
        vec.y = p0.y + (t * s1.y)
        return (True, vec)
    return (False, vec)

def doBouncePhysics(ball_pos, bv_frame, ball_velocity, start, end, n):
    ball_end = pygame.Vector2(ball_pos)
    ball_pos -= bv_frame
    intersection = getLineIntersection(ball_pos, ball_end, start, end)
    if intersection[0]:
        intersection[1]
        leftover =  ball_end - intersection[1]
        ball_velocity = ball_velocity.reflect(n)
        leftover = leftover.reflect(n)
        ball_pos = intersection[1] + leftover
        #print(f"Leftover: {leftover}, ball vel: {ball_velocity}, ball pos: {ball_pos}")

    return (ball_pos, ball_velocity)

def circleVsRectangle(circle_pos, circle_radius, rect_pos, rect_size):
    px = max(circle_pos.x, rect_pos.x)
    px = min(px, rect_pos.x + rect_size.x)
    py = max(circle_pos.y, rect_pos.y)
    py = min(py, rect_pos.y + rect_size.y)

    return (((circle_pos.y-py) ** 2 + (circle_pos.x-px) ** 2) < (circle_radius ** 2), pygame.Vector2(px, py))

did = circleVsRectangle(pygame.Vector2(0, 0), 5,
                  pygame.Vector2(10, 10), pygame.Vector2(8, 5))
print(f"{did}")
did = circleVsRectangle(pygame.Vector2(0, 0), 5,
                  pygame.Vector2(3, 3), pygame.Vector2(8, 5))
print(f"{did}")

isStepping = False
while running:
    procFrame = False
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if (event.key == pygame.K_F10):
                procFrame = True
            if (event.key == pygame.K_F9):
                isStepping = not isStepping

    keys = pygame.key.get_pressed()

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("black")

    pygame.draw.rect(screen, "white", ((player_pos), (player_size)), 40)
    pygame.draw.circle(screen, "white", ball_pos, 5)
    pygame.draw.circle(screen, "red", cube_center, 2)

    if not isStepping or (isStepping and procFrame):
        if keys[pygame.K_a]:
            player_pos.x -= 300 * dt
        if keys[pygame.K_d]:
            player_pos.x += 300 * dt

        cube_center.x = player_pos.x + 40
        cube_center.y = player_pos.y + 15

        if keys[pygame.K_SPACE] and not has_started:
            ball_velocity.x = ball_pos.x - cube_center.x
            ball_velocity.y = ball_pos.y - cube_center.y
            ball_velocity.normalize_ip()
            has_started = True

        bv_frame = ball_velocity * 350 * dt
        ball_pos += bv_frame

        collision, point = circleVsRectangle(ball_pos, 5, player_pos, player_size)
        if collision:
            pygame.draw.circle(screen, "red", point, 2)

        if ball_pos.x <= 0:
            ball_pos, ball_velocity = doBouncePhysics(ball_pos, bv_frame, ball_velocity,
                                                      pygame.Vector2(0,0), pygame.Vector2(0, screen.get_height()), 
                                                      pygame.Vector2(1,0))

        if ball_pos.y <= 0:
            ball_pos, ball_velocity = doBouncePhysics(ball_pos, bv_frame, ball_velocity, 
                                                      pygame.Vector2(0,0), pygame.Vector2(screen.get_width(), 0), 
                                                      pygame.Vector2(0,1))

        if ball_pos.x >= screen.get_width():
            ball_pos, ball_velocity = doBouncePhysics(ball_pos, bv_frame, ball_velocity,
                                                      pygame.Vector2(screen.get_width(), 0), pygame.Vector2(screen.get_width(), screen.get_height()),
                                                      pygame.Vector2(-1,0))

        if ball_pos.y >= screen.get_height():
            ball_pos, ball_velocity = doBouncePhysics(ball_pos, bv_frame, ball_velocity,
                                                      pygame.Vector2(screen.get_width(), screen.get_height()), pygame.Vector2(0, screen.get_height()), 
                                                      pygame.Vector2(0,-1))

    # flip() the display to put your work on screen
    pygame.display.flip()

    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(60) / 1000

pygame.quit()
