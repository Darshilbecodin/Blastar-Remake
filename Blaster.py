import pygame
import random
pygame.init()
clock = pygame.time.Clock()
SCREEN_WIDTH = 1024  
SCREEN_HEIGHT = 768
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
font = pygame.font.Font("data/PressStart2P.ttf", 24)

beam_sound = pygame.mixer.Sound("data/beamsound.wav")
beam_sound.set_volume(0.6)


pygame.mixer.music.load("data/Korobeiniki - 8-Bit Version.mp3")  # or .ogg, .wav
pygame.mixer.music.set_volume(0.5)  # optional: set volume (0.0 to 1.0)
pygame.mixer.music.play(-1)


#Sprites================================================
player = pygame.image.load("data/blastar0.png")
player = pygame.transform.scale(player, (36, 36))

alien = pygame.image.load("data/blastar2.png")
alien = pygame.transform.scale(alien, (36, 36))

status_beam = pygame.image.load("data/blastar4.png")
status_beam = pygame.transform.scale(status_beam, (36, 36))

blasted_ship = pygame.image.load("data/blastar5.png")
blasted_ship = pygame.transform.scale(blasted_ship, (36, 36))

bombs = pygame.image.load("data/blastar1.png")
bombs = pygame.transform.scale(bombs, (36, 36))

blasted_alien = pygame.image.load("data/blastar6.png")
blasted_alien = pygame.transform.scale(blasted_alien, (36, 36))

fellow_ship = pygame.image.load("data/Fellow_Ship.png")
fellow_ship = pygame.transform.scale(fellow_ship, (36, 36))
#positions================================================
playerx = 512 - 20

playery = 768 - 55

alienx = 20
alieny = 100

status_beamx = alienx
status_beamy = alieny

bombsx = playerx
bombsy = playery

beam_count = 0
beam_cooldown = False

fellowships = []
last_fellowship_score = 0

alien_spawn_chance = 0.1 # 10%
alien_spawn_increment_score = 600  # increase chance every 800 pts
last_alien_spawn_score = 0
#Events================================================
MOVE_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(MOVE_EVENT, 100)

ENCOUNTER_EVENT = pygame.USEREVENT + 2

Bomb_Event = pygame.USEREVENT + 3

Blast_Player_Event = pygame.USEREVENT + 4

BEAM_TIMER_EVENT = pygame.USEREVENT + 5

BEAM_SOUND_LOOP_EVENT = pygame.USEREVENT + 6

FELLOWSHIP_SPAWN_EVENT = pygame.USEREVENT + 7

ALIEN_SPAWN_EVENT = pygame.USEREVENT + 8

BLINK_EVENT = pygame.USEREVENT + 9
# ===========================================================
beam_active = False

stop_alien = False
stop_player = False
player_blasted = False
bomb_active = False
alien_blasted = False

ships_remaining = 5  # Number of ships remaining
score = 0


game_over = False
run = True


spawn_fellowship = False


respawning = False
blink_count = 0
blink_timer = 0
player_visible = True


# ================= Alien Manager =================
aliens = []

def create_alien(player_x, player_y):
    while True:
        rand_x = random.randint(20, SCREEN_WIDTH - 56)
        rand_y = random.randint(50, SCREEN_HEIGHT - 100)
        if abs(rand_x - player_x) >= 200 and abs(rand_y - player_y) >= 100:
            break
    return {
        "x": rand_x,
        "y": rand_y,
        "blasted": False,
        "beam_active": False,
        "beam_y": 0,
        "beam_count": 0
    }
# Start with one alien at the beginning of the game
first_alien = create_alien(playerx, playery)
first_alien["x"] = 20
first_alien["y"] = 100  # Force x to be 20 only for first alien
aliens.append(first_alien)


def spawn_random_fellowship():
    direction = random.choice(["rightward", "leftward"])
    y = random.randint(100, SCREEN_HEIGHT - 100)
    if direction == "rightward":
        x = -36  # just off left
    else:
        x = SCREEN_WIDTH  # just off right

    return {
        "x": x,
        "y": y,
        "direction": direction,
        "speed": random.randint(3, 10),
        "recruited": False
    }


def reset_beam():
    global beam_active, stop_alien, stop_player, attacking_alien_index
    if attacking_alien_index is not None and 0 <= attacking_alien_index < len(aliens):
        aliens[attacking_alien_index]["beam_y"] = aliens[attacking_alien_index]["y"]
        aliens[attacking_alien_index]["beam_count"] = 0
    beam_active = False
    stop_alien = False
    stop_player = False
    pygame.time.set_timer(BEAM_SOUND_LOOP_EVENT, 0)
    attacking_alien_index = None

max_aliens = 5
attacking_alien_index = None


pygame.time.set_timer(FELLOWSHIP_SPAWN_EVENT, 5000)
pygame.time.set_timer(ALIEN_SPAWN_EVENT, 7000)
# =============================================================================
while run:
    



    screen.fill((0, 0, 0)) 
    
     

    ship_text = font.render(f"Ships: {ships_remaining}", True, (255, 255, 255))
    screen.blit(ship_text, (412, 20))
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(score_text, (100, 20))
    
    game_over_text = font.render("FLEET DESTROYED", True, (255, 255, 255))
    another_game_text = font.render("WOULD YOU LIKE ANOTHER GAME? (Y/N)", True, (255, 255, 255))
    
    #If game over ================================================
    if game_over:
        ships_remaining = 0
        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 200))
        screen.blit(another_game_text, (SCREEN_WIDTH // 2 - 400, SCREEN_HEIGHT // 2 - 150))
        pygame.display.flip()

        if key[pygame.K_y]:
            game_over = False
            player_blasted = False
            alien_blasted = False
            playerx = 512 - 20
            playery = 768 - 55
            alienx = 20
            alieny = random.randint(50, 700)
            score = 0
            ships_remaining = 5
            stop_alien = False
            stop_player = False
        elif key[pygame.K_n]:
            run = False
            continue
    # spawning player =============================================================
    if player_blasted:
        screen.blit(blasted_ship, (playerx, playery))
    elif player_visible:
        screen.blit(player, (playerx, playery))
    # (Don't draw anything when player_visible is False)
    # spawning alien =============================================================
    for alien_data in aliens:
        if not alien_data["blasted"]:
            screen.blit(alien, (alien_data["x"], alien_data["y"]))
        else:
            screen.blit(blasted_alien, (alien_data["x"], alien_data["y"]))
    
    # defining rectangles for all sprites ========================================
    player_rect = player.get_rect(topleft=(playerx, playery))
    alien_rects = [alien.get_rect(topleft=(a["x"], a["y"])) for a in aliens]
    status_beam_rect = status_beam.get_rect(topleft=(alienx, alieny))
    bombs_rect = bombs.get_rect(topleft=(bombsx, bombsy))

    key = pygame.key.get_pressed()
    # Player movement =========================================================
    can_move = not stop_player or respawning  # Allow movement if respawning

    if key[pygame.K_a] and can_move:
        playerx = max(0, playerx - 10)
    if key[pygame.K_d] and can_move:
        playerx = min(SCREEN_WIDTH - 36, playerx + 10)
    if key[pygame.K_w] and can_move:
        playery = max(0, playery - 10)
    if key[pygame.K_s] and can_move:
        playery = min(SCREEN_HEIGHT - 36, playery + 10)
    
    if key[pygame.K_SPACE] and not player_blasted and not beam_active:
        bomb_active = True
        bombsx = playerx
        bombsy = playery
        
        

    #Beam mechanics ========================================================
    if beam_active and attacking_alien_index is not None:
        beam_text = font.render("Status Beam", True, (255, 255, 255))
        screen.blit(beam_text, (700, 384))

        aliens[attacking_alien_index]["beam_y"] += 10
        beam_rect = status_beam.get_rect(topleft=(aliens[attacking_alien_index]["x"], aliens[attacking_alien_index]["beam_y"]))
        screen.blit(status_beam, beam_rect)

        if beam_rect.colliderect(player_rect):
            player_blasted = True
            reset_beam()
            ships_remaining -= 1

            screen.fill((0, 0, 0))
            screen.blit(blasted_ship, (playerx, playery))
            for alien_data in aliens:
                if not alien_data["blasted"]:
                    screen.blit(alien, (alien_data["x"], alien_data["y"]))
                else:
                    screen.blit(blasted_alien, (alien_data["x"], alien_data["y"]))
            screen.blit(ship_text, (412, 20))
            screen.blit(score_text, (100, 20))
            pygame.display.flip()
            pygame.time.delay(1000)


            # after collision with beam, checking if game is over or not.
            if ships_remaining > 0:
                playerx = 512 - 20
                playery = 768 - 55
                respawning = True
                blink_count = 0
                player_visible = False
                pygame.time.set_timer(BLINK_EVENT, 300)
                player_blasted = False
            else:
                game_over = True

            # ✅ Clear beam logic regardless of game over or respawn
            reset_beam()
            

            
        elif aliens[attacking_alien_index]["beam_y"] > SCREEN_HEIGHT:
            if aliens[attacking_alien_index]["beam_count"] < 2:
                aliens[attacking_alien_index]["beam_count"] += 1
                aliens[attacking_alien_index]["beam_y"] = aliens[attacking_alien_index]["y"]
            else: # If the beam doesnt hit the player after 3 attempts, reset the beam and alien moves on
                beam_active = False
                stop_alien = False
                stop_player = False
                aliens[attacking_alien_index]["beam_count"] = 0
                attacking_alien_index = None
                pygame.time.set_timer(BEAM_SOUND_LOOP_EVENT, 0)

    #bomb mechanics ========================================================
    if bomb_active and not beam_active and not player_blasted and not alien_blasted and not respawning:
        bombsy -= 10
        screen.blit(bombs, (bombsx, bombsy))
        for i, alien_rect in enumerate(alien_rects):
             if bombs_rect.colliderect(alien_rect) and not aliens[i]["blasted"]:
                aliens[i]["blasted"] = True
                score += 80

                if score >= last_alien_spawn_score + alien_spawn_increment_score:
                    alien_spawn_chance = min(alien_spawn_chance + 0.1, 1.0)  # max 100%
                    last_alien_spawn_score = score
                screen.fill((0, 0, 0))
                for alien_data in aliens:
                    if not alien_data["blasted"]:
                        screen.blit(alien, (alien_data["x"], alien_data["y"]))
                    else:
                        screen.blit(blasted_alien, (alien_data["x"], alien_data["y"]))
                screen.blit(ship_text, (412, 20))
                screen.blit(score_text, (100, 20))
                screen.blit(player, (playerx, playery))
                pygame.display.flip()
                pygame.time.delay(1000)

                # Reset alien
                alien_blasted = False
                aliens[i] = create_alien(playerx, playery)
                # playerx = 512 - 20
                # playery = 768 - 55
                bomb_active = False
            
    # if both bomb and beam are active, deactivate the bomb
    if bomb_active and beam_active:
        bomb_active = False

    # remove bomb when it goes off-screen
    if bombsy < 0:
        bomb_active = False  
    # encounter event =================================================   
    for i, alien_rect in enumerate(alien_rects):
        if abs(player_rect.x - alien_rect.x) < 5 and not beam_active and not aliens[i]["blasted"] and playery > aliens[i]["y"] and not respawning:
            pygame.event.post(pygame.event.Event(ENCOUNTER_EVENT, {"alien_index": i}))
            break
            # Resetting the alien beam if it goes off-screen

    if score >= last_fellowship_score + 400:
        fellowships.append(spawn_random_fellowship())
        last_fellowship_score += 400

    # event handling =================================================
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        elif event.type == MOVE_EVENT and not stop_alien:
            for alien_data in aliens:
                if not alien_data["blasted"]:
                    alien_data["x"] += 10
                    if alien_data["x"] > SCREEN_WIDTH:
                        alien_data["x"] = 20
                
        elif event.type == ENCOUNTER_EVENT:
            attacking_alien_index = event.dict["alien_index"]
            beam_active = True
            aliens[attacking_alien_index]["beam_y"] = aliens[attacking_alien_index]["y"]
            stop_alien = True    
            stop_player = True
            pygame.time.set_timer(BEAM_SOUND_LOOP_EVENT, 500)
            
            

        elif event.type == BEAM_SOUND_LOOP_EVENT and beam_active:
            beam_sound.play()   

        elif event.type == FELLOWSHIP_SPAWN_EVENT:
            if random.random() < 0.1:  # 40% chance every 3 sec
                fellowships.append(spawn_random_fellowship())
            
        elif event.type == ALIEN_SPAWN_EVENT:
            # Increase max_aliens as score increases (up to 10)
            max_aliens = min(5 + score // 500, 10)
            active_aliens = [a for a in aliens if not a["blasted"]]
            if random.random() < alien_spawn_chance and len(active_aliens) < max_aliens:
                aliens.append(create_alien(playerx, playery))    

        elif event.type == BLINK_EVENT and respawning:
            blink_count += 1
            player_visible = not player_visible

            if blink_count >= 6:
                respawning = False
                player_visible = True
                player_blasted = False
                stop_player = False
                stop_alien = False
                pygame.time.set_timer(BLINK_EVENT, 0)   
       

    for ship in fellowships:
        if not ship["recruited"]:
            # Move
            if ship["direction"] == "rightward":
                ship["x"] += ship["speed"]
            else:
                ship["x"] -= ship["speed"]

            # Draw
            screen.blit(fellow_ship, (ship["x"], ship["y"]))

            # Collision with player
            ship_rect = fellow_ship.get_rect(topleft=(ship["x"], ship["y"]))
            if ship_rect.colliderect(player_rect):
                ship["recruited"] = True
                ships_remaining += 1  

    pygame.display.flip()
    clock.tick(20)

pygame.quit()