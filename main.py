# TODO:
# Player velocity
import pygame

# pygame setup
pygame.init()
pygame.font.init()
pygame.mixer.init()
pygame.mixer.music.load("./data/1. Feels Like Winning.wav")
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(0.1)
sys_font = pygame.font.Font(None, 40)
bump_sfx = pygame.mixer.Sound("./data/bump.wav")
screen = pygame.display.set_mode((1920, 1080))
clock = pygame.time.Clock()
running = True
dt = 0
award_amount = 5
score = 0
multiplyer = 1

walls = []
# Left
walls.append(pygame.Rect((-20, 0), (20, screen.get_height())))
# Top
walls.append(pygame.Rect((0, -20), (screen.get_width(), 20)))
# Right
walls.append(pygame.Rect((screen.get_width(), 0), (20, screen.get_height())))

player_pos = pygame.Vector2(screen.get_width() / 2 - 80, screen.get_height() - 80)
player_size = pygame.Vector2(160, 60)
player_velocity = pygame.Vector2(0,0)
cube_center = player_pos + (player_size * 0.5)
ball_pos = pygame.Vector2(screen.get_width() / 2, screen.get_height() - 100)
ball_radius = 10
ball_velocity = pygame.Vector2(0, 0)
has_started = False
x_count = 11
y_count = 6
block_size = pygame.Vector2(150, 50)
blocks = []

def init_blocks():
    start_x = (screen.get_width() - (x_count * player_size.x)) / 2 
    start_y = 355
    for y in range(y_count):
        for x in range(x_count):
            blocks.append(pygame.Rect((start_x, start_y), block_size))
            start_x += player_size.x
        start_y -= player_size.y
        start_x = (screen.get_width() - (x_count * player_size.x)) / 2 
init_blocks()
block_colors = ["purple", "blue", "green", "yellow", "orange", "red"]

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

def doBouncePhysics(ball_pos, ball_velocity, intersect_point, n):
    leftover = (ball_pos - intersect_point).magnitude() - (ball_radius * 1.001)
    ball_pos += (leftover * ball_velocity)
    ball_velocity = ball_velocity.reflect(n)
    return ball_pos, ball_velocity

def doBounceOffPlayer(ball_pos, ball_velocity, intersect_point, n, center_rect):
    print(f"bp {ball_pos} bv {ball_velocity}")
    diff_dir = (intersect_point - center_rect).normalize()
    print(f"{diff_dir}")
    leftover = (ball_pos - intersect_point).magnitude() - (ball_radius * 1.001)
    print(f"{leftover}")
    ball_pos += (leftover * ball_velocity)
    print(f"new ballpos {ball_pos}")
    ball_velocity = (ball_velocity.reflect(n) + diff_dir).normalize()
    print(f"new ball vel: {ball_velocity}")
    return ball_pos, ball_velocity

def doBounceOffPlayer2(ball_pos, ball_velocity, player_velocity, intersect_point, n, center_rect):
    print(f"bp {ball_pos} bv {ball_velocity} pv {player_velocity}")
    #diff_dir = (intersect_point - center_rect).normalize()
    leftover = (ball_radius * 1.001) - (ball_pos - intersect_point).magnitude()
    print(f"{leftover}")
    ball_pos += (leftover * player_velocity)
    print(f"new ballpos {ball_pos}")
    #ball_velocity = (ball_velocity.reflect(n) + diff_dir).normalize()
    ball_velocity = ball_velocity.reflect(n)
    print(f"new ball vel: {ball_velocity}")
    return ball_pos, ball_velocity

def circleVsRectangle(circle_pos, circle_radius, rect):
    px = max(circle_pos.x, rect.x)
    px = min(px, rect.x + rect.w)
    py = max(circle_pos.y, rect.y)
    py = min(py, rect.y + rect.h)

    return (((circle_pos.y-py) ** 2 + (circle_pos.x-px) ** 2) < (circle_radius ** 2), pygame.Vector2(px, py))

def findFaceNormal(ball_center, rect):
    rect_center = pygame.Vector2(rect.x + (rect.w * 0.5), rect.y + (rect.h * 0.5))
    top_left = pygame.Vector2(rect.x, rect.y)
    top_right = pygame.Vector2(rect.x + rect.w, rect.y)
    bot_left = pygame.Vector2(rect.x, rect.y + rect.h)
    bot_right = pygame.Vector2(rect.x + rect.w, rect.y + rect.h)

    # Test top line
    intersection = getLineIntersection(ball_center, rect_center, top_left, top_right)
    if intersection[0]:
        return pygame.Vector2(0, 1)
    
    # Test right line
    intersection = getLineIntersection(ball_center, rect_center, top_right, bot_right)
    if intersection[0]:
        return pygame.Vector2(1, 0)

    # Test bottom line
    intersection = getLineIntersection(ball_center, rect_center, bot_left, bot_right)
    if intersection[0]:
        return pygame.Vector2(0, -1)

    # Test left line
    intersection = getLineIntersection(ball_center, rect_center, bot_left, top_left)
    if intersection[0]:
        return pygame.Vector2(-1, 0)

    return pygame.Vector2(0, 0)

collision = False
isStepping = False
game_over = False
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
    pygame.draw.circle(screen, "white", ball_pos, ball_radius)
    pygame.draw.circle(screen, "red", cube_center, 2)
    
    for y in range(y_count):
        color = block_colors[y]
        for x in range(x_count):
            #print(f"index: {y * x_count + x}, color: {color}, rect: {blocks[y * x_count + x]}")
            pygame.draw.rect(screen, color, blocks[y * x_count + x])

    font_img = sys_font.render(f"Score: {score}", True, "white")
    screen.blit(font_img, (screen.get_width() / 2 - font_img.get_width() / 2, 5))

    cube_center = player_pos + (player_size * 0.5)

    if (not isStepping or (isStepping and procFrame)):
        player_velocity.update(0, 0)
        if keys[pygame.K_a]:
            player_velocity.x = -1
        if keys[pygame.K_d]:
            player_velocity.x = 1

        player_pos += player_velocity * 300 * dt

        if player_pos.x < 0:
            player_pos.x = 0
        if player_pos.x > screen.get_width() - player_size.x:
            player_pos.x = screen.get_width() - player_size.x

        p_rect = pygame.Rect(player_pos, player_size)
        #dc, contact_point = circleVsRectangle(ball_pos, ball_radius, p_rect)
        #if dc:
        #    print("player hit the ball!")
        #    normal = findFaceNormal(ball_pos, p_rect)
        #    print(f"player normal {normal}")
        #    ball_pos, ball_velocity = doBounceOffPlayer2(ball_pos, ball_velocity, player_velocity, contact_point, normal, p_rect.center)
        #    # TODO: check physics?
        #    ball_pos += ball_velocity * 350 * dt
        #    multiplyer = 1

        if keys[pygame.K_SPACE] and not has_started:
            print("START")
            score = 0
            ball_velocity.x = ball_pos.x - cube_center.x
            ball_velocity.y = ball_pos.y - cube_center.y
            ball_velocity.normalize_ip()
            has_started = True
            game_over = False

        bv_frame = ball_velocity * 350 * dt
        ball_pos += bv_frame

        for y in range(y_count):
            for x in range(x_count):
                b = blocks[y * x_count + x]
                dc, contact_point = circleVsRectangle(ball_pos, ball_radius, b)
                if dc:
                    normal = findFaceNormal(ball_pos, b)
                    ball_pos -= bv_frame
                    ball_pos, ball_velocity = doBouncePhysics(ball_pos, ball_velocity, contact_point, normal)
                    bump_sfx.play()
                    score += (award_amount * y + award_amount) * multiplyer
                    multiplyer = 2
                    print(f"multiplyer {multiplyer}")
                    b.update(-10, -10, 1, 1)

        dc, contact_point = circleVsRectangle(ball_pos, ball_radius, p_rect)
        if dc:
            print("Ball hit player!")
            normal = findFaceNormal(ball_pos, p_rect)
            print(f"{normal}")
            ball_pos -= bv_frame
            ball_pos, ball_velocity = doBounceOffPlayer(ball_pos, ball_velocity, contact_point, normal, p_rect.center)
            bump_sfx.play()
            multiplyer = 1

        for w in walls:
            dc, contact_point = circleVsRectangle(ball_pos, ball_radius, w)
            if dc:
                normal = findFaceNormal(ball_pos, w)
                ball_pos -= bv_frame
                ball_pos, ball_velocity = doBouncePhysics(ball_pos, ball_velocity, contact_point, normal)
                bump_sfx.play()

        if ball_pos.y >= screen.get_height():
            game_over = True
            ball_velocity.update(0, 0)
            has_started = False
            player_pos.update(screen.get_width() / 2 - 80, screen.get_height() - 80)
            ball_pos.update(screen.get_width() / 2, screen.get_height() - 100)
            blocks.clear()
            init_blocks()

    # flip() the display to put your work on screen
    pygame.display.flip()

    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(60) / 1000

pygame.quit()
