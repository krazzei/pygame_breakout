# Example file showing a circle moving on screen
import pygame

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
dt = 0

player_pos = pygame.Vector2(screen.get_width() / 2 - 40, screen.get_height() - 40)
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

tup = getLineIntersection(pygame.Vector2(1, 0), pygame.Vector2(0, 1), pygame.Vector2(0, 0), pygame.Vector2(1,1))
print(f"Did intersect {tup[0]}, point {tup[1]}")
tup = getLineIntersection(pygame.Vector2(2, 0), pygame.Vector2(2, 2), pygame.Vector2(-1, 0), pygame.Vector2(-1, 3))
print(f"Did intersect {tup[0]}, point {tup[1]}")

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("black")

    pygame.draw.rect(screen, "white", ((player_pos), (80, 30)), 40)
    pygame.draw.circle(screen, "white", ball_pos, 5)
    pygame.draw.circle(screen, "red", cube_center, 2)

    keys = pygame.key.get_pressed()
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
    #ball_pos.x += ball_velocity.x * 350 * dt
    #ball_pos.y += ball_velocity.y * 350 * dt

    if ball_pos.x <= 0:
        print(f"{ball_pos}")
        ball_end = pygame.Vector2(ball_pos)
        ball_pos -= bv_frame
        print(f"testing line {ball_pos} {ball_end} against (0,0) (0,{screen.get_height()})")
        intersection = getLineIntersection(ball_pos, ball_end, pygame.Vector2(0,0), pygame.Vector2(0, screen.get_height()))
        print(f"intersection: {intersection}")
        if intersection[0]:
            print("got intersection")
            intersection[1]
            leftover =  ball_end - intersection[1]
            n = pygame.Vector2(1,0)
            ball_velocity = ball_velocity.reflect(n)
            leftover = leftover.reflect(n)
            ball_pos = intersection[1] + leftover
            print(f"Leftover: {leftover}, ball vel: {ball_velocity}, ball pos: {ball_pos}")

        #print("ball moved this frame: ", 350 * dt)
        #print("ball moved on x this frame: ", ball_velocity.x * 350 * dt)
        ## get leftover velocity
        #leftover = ball_pos.x * -1
        #factor = () / (ball_pos.x - ball_end.x)
        ## change velocity vector (reflect?)
        #n = pygame.Vector2(1,0)
        #ball_velocity = ball_velocity.reflect(n)
        ## move more with new velocity.
        #p = leftover / (350 * dt)
        #print("correction this frame: ", p * (350 * dt))
        #ball_pos.x += ball_velocity.x * p * (350 * dt)

    if ball_pos.y <= 0:
        leftover = ball_pos.y * -1
        n = pygame.Vector2(0, 1)
        ball_velocity = ball_velocity.reflect(n)
        p = leftover / (350 * dt)
        ball_pos.y += ball_velocity.y * p * (350 * dt)

    if ball_pos.x >= screen.get_width():
        leftover = ball_pos.x - screen.get_width()
        print("Leftover: ", leftover)
        n = pygame.Vector2(-1, 0)
        ball_velocity = ball_velocity.reflect(n)
        p = leftover / (350 * dt)
        ball_pos.x += ball_velocity.x * p * (350 * dt)

    if ball_pos.y >= screen.get_height():
        leftover = ball_pos.y - screen.get_height()
        print("Leftover: ", leftover)
        n = pygame.Vector2(0, -1)
        ball_velocity = ball_velocity.reflect(n)
        p = leftover / (350 * dt)
        ball_pos.y += ball_velocity.y * p * (350 * dt)

    # flip() the display to put your work on screen
    pygame.display.flip()

    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(165) / 1000

pygame.quit()
