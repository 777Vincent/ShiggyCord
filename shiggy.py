import pygame
import sys
import win32gui
import win32con
import keyboard
import pygetwindow as gw
import random

# Function to check if any window is focused
def is_any_window_focused():
    active_window = gw.getActiveWindow()
    return active_window is not None

# Function to check if Discord window is focused
def is_discord_focused():
    active_window = gw.getActiveWindow()
    if active_window is not None and "Discord" in active_window.title:
        return True
    return False

# Function to get the size of the Discord window
def get_discord_window_rect():
    try:
        discord_window = gw.getWindowsWithTitle("Discord")[0]
        return discord_window.left, discord_window.top, discord_window.width, discord_window.height
    except IndexError:
        # If the Discord window is closed, return a default rectangle
        return 0, 0, 0, 0

# Initialize Pygame
pygame.init()

# Get the initial position and size of the Discord window
discord_left, discord_top, discord_width, discord_height = get_discord_window_rect()

# Set initial display position and size to match Discord window
display_width = discord_width
display_height = discord_height

# Create a transparent display
game_display = pygame.display.set_mode((display_width, display_height), pygame.NOFRAME)
hwnd = pygame.display.get_wm_info()["window"]
win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
                        win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT | win32con.WS_EX_NOACTIVATE)
win32gui.SetLayeredWindowAttributes(hwnd, 0, 255, win32con.LWA_COLORKEY)
pygame.display.set_caption('shiggycord')
pygame.display.update()

# Load the gif frames
gif_frames = []
for i in range(1, 10):  # Loading frames 1 to 9
    frame = pygame.image.load(f"shiggyframe ({i}).gif")
    frame = pygame.transform.scale(frame, (100, 100))
    gif_frames.append(frame)

# Get the dimensions of the gif
gif_width, gif_height = gif_frames[0].get_size()

# List to store shiggy objects
shiggies = []

# Set frame delay
frame_delay = 20  # milliseconds

# Define the callback function for the hotkey
def handle_hotkey():
    pygame.quit()
    sys.exit()

# Flag to track if hotkey is being held down
hotkey_pressed = False

# Function to create a new shiggy object
def spawn_shiggy(x, y):
    speed_x = random.choice([-1, 1])  # Randomize initial direction
    speed_y = random.choice([-1, 1])  # Randomize initial direction
    frame_index = random.randint(0, len(gif_frames) - 1)  # Randomize initial frame
    shiggies.append({'x': x, 'y': y, 'speed_x': speed_x, 'speed_y': speed_y, 'frame_index': frame_index})

# Spawn the initial shiggy at a random position
spawn_shiggy(random.randint(0, display_width - gif_width), random.randint(0, display_height - gif_height))

# Main loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Limit frame rate
    pygame.time.wait(frame_delay)

    # Get the current position and size of the Discord window
    current_discord_left, current_discord_top, current_discord_width, current_discord_height = get_discord_window_rect()

    # Update display position and size if Discord window changes
    if current_discord_left != discord_left or current_discord_top != discord_top or \
       current_discord_width != display_width or current_discord_height != display_height:
        discord_left = current_discord_left
        discord_top = current_discord_top
        display_width = current_discord_width
        display_height = current_discord_height
        game_display = pygame.display.set_mode((display_width, display_height), pygame.NOFRAME)

        if display_width == 0 or display_height == 0 or not is_any_window_focused():
            # If no window is focused, hide the Pygame window
            game_display.fill((0, 0, 0))
            pygame.display.update()
            continue

        win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, discord_left, discord_top, display_width, display_height,
                               win32con.SWP_SHOWWINDOW)

    # Check if Discord is focused
    if is_discord_focused():
        # Set window to always on top
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, discord_left, discord_top, display_width, display_height,
                               win32con.SWP_SHOWWINDOW)

        # Check for hotkey
        if keyboard.is_pressed('ctrl') and keyboard.is_pressed('alt') and keyboard.is_pressed('f'):
            handle_hotkey()

        # Check if Ctrl+Shift+J is pressed to spawn a single shiggy
        if keyboard.is_pressed('ctrl') and keyboard.is_pressed('shift') and keyboard.is_pressed('j') and not hotkey_pressed:
            spawn_shiggy(random.randint(0, display_width - gif_width), random.randint(0, display_height - gif_height))
            hotkey_pressed = True

        # Check if Ctrl+Shift+K is pressed to spawn multiple shiggies
        if keyboard.is_pressed('ctrl') and keyboard.is_pressed('shift') and keyboard.is_pressed('k') and not hotkey_pressed:
            for _ in range(5):  # Spawn 5 shiggies
                spawn_shiggy(random.randint(0, display_width - gif_width), random.randint(0, display_height - gif_height))
            hotkey_pressed = True

        # Check if Shift+Esc is pressed to clear all shiggies
        if keyboard.is_pressed('shift') and keyboard.is_pressed('esc') and not hotkey_pressed:
            shiggies.clear()
            hotkey_pressed = True

        # Check if hotkey is released
        if not keyboard.is_pressed('j') and not keyboard.is_pressed('k') and not keyboard.is_pressed('esc'):
            hotkey_pressed = False

        # Clear the display
        game_display.fill((0, 0, 0))

        # Update and draw all shiggy objects
        for shiggy in shiggies:
            shiggy['x'] += shiggy['speed_x']
            shiggy['y'] += shiggy['speed_y']

            # Bounce off the walls
            if shiggy['x'] + gif_width > display_width or shiggy['x'] < 0:
                shiggy['speed_x'] = -shiggy['speed_x']
            if shiggy['y'] + gif_height > display_height or shiggy['y'] < 0:
                shiggy['speed_y'] = -shiggy['speed_y']

            # Ensure the entire shiggy stays within the window boundaries
            shiggy['x'] = max(0, min(shiggy['x'], display_width - gif_width))
            shiggy['y'] = max(0, min(shiggy['y'], display_height - gif_height))

            # Increment frame index for animation
            shiggy['frame_index'] = (shiggy['frame_index'] + 1) % len(gif_frames)

            # Draw the current frame of the shiggy
            game_display.blit(gif_frames[shiggy['frame_index']], (shiggy['x'], shiggy['y']))

        # Update the display
        pygame.display.update()
    else:
        # If Discord is not focused, clear the display
        game_display.fill((0, 0, 0))
        pygame.display.update()
