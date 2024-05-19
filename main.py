# TODO:
# Clamp player movement to screen
# Sounds
# Score
# Block layout margin
# Player velocity
import pygame

# pygame setup
pygame.init()
pygame.font.init()
screen = pygame.display.set_mode((1920, 1080))
clock = pygame.time.Clock()
running = True
dt = 0

player_pos = pygame.Vector2(screen.get_width() / 2 - 80, screen.get_height() - 80)
player_size = pygame.Vector2(160, 60)
cube_center = player_pos + (player_size) #pygame.Vector2(player_pos.x + 40, player_pos.y + 15)
ball_pos = pygame.Vector2(screen.get_width() / 2, screen.get_height() - 100)
ball_velocity = pygame.Vector2(0, 0)
has_started = False
start_x = 50
start_y = 25
x_count = 11
y_count = 6
block_size = pygame.Vector2(150, 50)
blocks = []
for y in range(y_count):
    for x in range(x_count):
        blocks.append(pygame.Rect((start_x, start_y), block_size))
        start_x += player_size.x
    start_y += player_size.y
    start_x = 50

block_colors = ["red", "orange", "yellow", "green", "blue", "purple"]

def getLineIntersection(p0: pygame.Vector2, p1: pygame.Vector2, p2: pygame.Vector2, p3: pygame.Vector2):
    vec = pygame.Vector2(0,0)
    s1 = p1 - p0
    s2 = p3 - p2

    denom = (-s2.x * s1.y + s1.x * s2.y)
    if denom == 0:
        #print("denom is 0")
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

def circleVelocityVsRectangle(ball_pos, bv_frame, ball_velocity, rect_point, rect_size):
    did_collide = False
    ball_end = pygame.Vector2(ball_pos)
    ball_start = (ball_pos - bv_frame)
    topRight = pygame.Vector2(rect_point.x + rect_size.x, rect_point.y)
    botLeft = pygame.Vector2(rect_point.x, rect_point.y + rect_size.y)
    n = pygame.Vector2(0, 1)
    intersection = getLineIntersection(ball_start, ball_end, rect_point, topRight)
    if intersection[0]:
        did_collide = True 
        print("intersect top line")
        leftover =  ball_end - intersection[1]
        ball_velocity = ball_velocity.reflect(n)
        leftover = leftover.reflect(n)
        ball_pos = intersection[1] + leftover

    n.update(1, 0)
    intersection = getLineIntersection(ball_start, ball_end, topRight, rect_point + rect_size)
    if intersection[0]:
        did_collide = True 
        print("intersect right line")
        leftover =  ball_end - intersection[1]
        ball_velocity = ball_velocity.reflect(n)
        leftover = leftover.reflect(n)
        ball_pos = intersection[1] + leftover

    n.update(0, -1)
    intersection = getLineIntersection(ball_start, ball_end, rect_point + rect_size, botLeft)
    if intersection[0]:
        did_collide = True 
        print("intersect bottom line")
        leftover =  ball_end - intersection[1]
        ball_velocity = ball_velocity.reflect(n)
        leftover = leftover.reflect(n)
        ball_pos = intersection[1] + leftover

    n.update(-1, 0)
    intersection = getLineIntersection(ball_start, ball_end, botLeft, rect_point)
    if intersection[0]:
        did_collide = True 
        print("intersect left line")
        leftover =  ball_end - intersection[1]
        ball_velocity = ball_velocity.reflect(n)
        leftover = leftover.reflect(n)
        ball_pos = intersection[1] + leftover
    
    return (ball_pos, ball_velocity, did_collide)

def circleVelocityVsPlayerRectangle(ball_pos, bv_frame, ball_velocity, rect_point, rect_size):
    radius_correction = ball_velocity * 5
    ball_end = pygame.Vector2(ball_pos)# - radius_correction
    ball_start = (ball_pos - bv_frame)# + radius_correction
    topRight = pygame.Vector2(rect_point.x + rect_size.x, rect_point.y)
    botLeft = pygame.Vector2(rect_point.x, rect_point.y + rect_size.y)
    center_rect = rect_point + (rect_size * 0.5)
    n = pygame.Vector2(0, 1)
    intersection = getLineIntersection(ball_start, ball_end, rect_point, topRight)
    if intersection[0]:
        diff_dir = (intersection[1] - center_rect).normalize()
        leftover =  ball_end - intersection[1]# + radius_correction
        ball_velocity = (ball_velocity.reflect(n) + diff_dir).normalize()
        leftover = leftover.reflect(n)
        ball_pos = intersection[1] + leftover
        #return (ball_pos, ball_velocity)

    n.update(1, 0)
    intersection = getLineIntersection(ball_start, ball_end, topRight, rect_point + rect_size)
    if intersection[0]:
        diff_dir = (intersection[1] - center_rect).normalize()
        leftover =  ball_end - intersection[1]# + radius_correction
        ball_velocity = (ball_velocity.reflect(n) + diff_dir).normalize()
        leftover = leftover.reflect(n)
        ball_pos = intersection[1] + leftover
        #return (ball_pos, ball_velocity)

    n.update(0, -1)
    intersection = getLineIntersection(ball_start, ball_end, rect_point + rect_size, botLeft)
    if intersection[0]:
        diff_dir = (intersection[1] - center_rect).normalize()
        leftover =  ball_end - intersection[1]# + radius_correction
        ball_velocity = (ball_velocity.reflect(n) + diff_dir).normalize()
        leftover = leftover.reflect(n)
        ball_pos = intersection[1] + leftover
        #return (ball_pos, ball_velocity)

    n.update(-1, 0)
    intersection = getLineIntersection(ball_start, ball_end, botLeft, rect_point)
    if intersection[0]:
        diff_dir = (intersection[1] - center_rect).normalize()
        leftover =  ball_end - intersection[1]# + radius_correction
        ball_velocity = (ball_velocity.reflect(n) + diff_dir).normalize()
        leftover = leftover.reflect(n)
        ball_pos = intersection[1] + leftover
        #return (ball_pos, ball_velocity)
    
    return (ball_pos, ball_velocity)

collision = False
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

    pygame.draw.rect(screen, "white", ((player_pos), (player_size)))
    pygame.draw.circle(screen, "white", ball_pos, 10)
    pygame.draw.circle(screen, "red", cube_center, 2)

    for y in range(y_count):
        color = block_colors[y]
        for x in range(x_count):
            #print(f"index: {y * x_count + x}, color: {color}, rect: {blocks[y * x_count + x]}")
            pygame.draw.rect(screen, color, blocks[y * x_count + x])

    if not isStepping or (isStepping and procFrame):
        # TODO: player velocity, player vs ball collision check.
        if keys[pygame.K_a]:
            player_pos.x -= 300 * dt
        if keys[pygame.K_d]:
            player_pos.x += 300 * dt

        cube_center = player_pos + (player_size * 0.5)

        if keys[pygame.K_SPACE] and not has_started:
            print("START")
            ball_velocity.x = ball_pos.x - cube_center.x
            ball_velocity.y = ball_pos.y - cube_center.y
            ball_velocity.normalize_ip()
            has_started = True

        bv_frame = ball_velocity * 350 * dt
        ball_pos += bv_frame

        for y in range(y_count):
            for x in range(x_count):
                b = blocks[y * x_count + x]
                ball_pos, ball_velocity, did_collide = circleVelocityVsRectangle(ball_pos, bv_frame, ball_velocity,
                                                                    pygame.Vector2(b.x, b.y),
                                                                    pygame.Vector2(b.w, b.h))
                if did_collide:
                    blocks[y * x_count + x].update(-10, -10, 1, 1)


        ball_pos, ball_velocity = circleVelocityVsPlayerRectangle(ball_pos, bv_frame, ball_velocity, 
                                                            player_pos, player_size)
        
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
    #print(f"{dt}ms")

pygame.quit()
