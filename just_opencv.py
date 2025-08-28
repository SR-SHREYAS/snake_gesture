import cv2
import mediapipe as mp
from snake_game import start_game

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

game = start_game()

WINDOW_NAME = 'Hand Tracking'
cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)

windows_positioned = False
restart_btn_rect = None  # (x1, y1, x2, y2)

def position_windows(frame_width, frame_height):
    global windows_positioned
    if windows_positioned:
        return
    try:
        screen_w = game.window.winfo_screenwidth()
        screen_h = game.window.winfo_screenheight()

        left_x = 50
        left_y = 50

        right_x = min(left_x + int(screen_w * 0.5), max(0, screen_w - frame_width - 50))
        right_y = left_y

        # Position Tkinter window on the left
        gw = game.window.winfo_width()
        gh = game.window.winfo_height()
        game.window.geometry(f"{gw}x{gh}+{left_x}+{left_y}")

        # Position OpenCV window on the right
        cv2.resizeWindow(WINDOW_NAME, frame_width, frame_height)
        cv2.moveWindow(WINDOW_NAME, right_x, right_y)

        windows_positioned = True
    except Exception:
        pass

def draw_restart_overlay(frame):
    global restart_btn_rect
    h, w = frame.shape[:2]
    overlay = frame.copy()

    # Dim background
    cv2.rectangle(overlay, (0, 0), (w, h), (0, 0, 0), -1)
    alpha = 0.5
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

    # Button dimensions
    btn_w = int(w * 0.5)
    btn_h = int(h * 0.12)
    x1 = (w - btn_w) // 2
    y1 = (h - btn_h) // 2
    x2 = x1 + btn_w
    y2 = y1 + btn_h

    restart_btn_rect = (x1, y1, x2, y2)

    # Button background and border
    cv2.rectangle(frame, (x1, y1), (x2, y2), (30, 144, 255), -1)
    cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 255), 3)

    # Text
    text = 'Game Over - Press R or Click to Restart'
    font = cv2.FONT_HERSHEY_SIMPLEX
    scale = 0.8
    thickness = 2
    (tw, th), _ = cv2.getTextSize(text, font, scale, thickness)
    tx = x1 + (btn_w - tw) // 2
    ty = y1 + (btn_h + th) // 2 - 5
    cv2.putText(frame, text, (tx, ty), font, scale, (0, 0, 0), thickness, cv2.LINE_AA)

def mouse_callback(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        if getattr(game, 'is_game_over', False) and restart_btn_rect is not None:
            x1, y1, x2, y2 = restart_btn_rect
            if x1 <= x <= x2 and y1 <= y <= y2:
                game.restart()
                # Reposition after restart too
                fw = param.get('frame_width')
                fh = param.get('frame_height')
                position_windows(fw, fh)

cv2.setMouseCallback(WINDOW_NAME, mouse_callback, param={'frame_width': 640, 'frame_height': 480})

def compute_overlay_geometry(width, height):
    radius = int(min(width, height) * 0.10)
    centers = {
        'up':    (int(width * 0.50), int(height * 0.20)),
        'down':  (int(width * 0.50), int(height * 0.80)),
        'left':  (int(width * 0.20), int(height * 0.50)),
        'right': (int(width * 0.80), int(height * 0.50)),
    }
    return centers, radius

def draw_direction_pad(frame, centers, radius, active_direction=None):
    color_idle = (100, 100, 100)
    color_active = (0, 255, 255)

    # Draw circles
    for direction, (cx, cy) in centers.items():
        is_active = (direction == active_direction)
        color = color_active if is_active else color_idle
        thickness = 4 if is_active else 2
        cv2.circle(frame, (cx, cy), radius, color, thickness)

    # Draw arrows inside circles
    arrow_len = int(radius * 0.6)
    base_thickness = 3
    # Up
    cx, cy = centers['up']
    cv2.arrowedLine(frame, (cx, cy + arrow_len // 2), (cx, cy - arrow_len // 2), color_active if active_direction=='up' else color_idle, base_thickness + (1 if active_direction=='up' else 0), tipLength=0.5)
    # Down
    cx, cy = centers['down']
    cv2.arrowedLine(frame, (cx, cy - arrow_len // 2), (cx, cy + arrow_len // 2), color_active if active_direction=='down' else color_idle, base_thickness + (1 if active_direction=='down' else 0), tipLength=0.5)
    # Left
    cx, cy = centers['left']
    cv2.arrowedLine(frame, (cx + arrow_len // 2, cy), (cx - arrow_len // 2, cy), color_active if active_direction=='left' else color_idle, base_thickness + (1 if active_direction=='left' else 0), tipLength=0.5)
    # Right
    cx, cy = centers['right']
    cv2.arrowedLine(frame, (cx - arrow_len // 2, cy), (cx + arrow_len // 2, cy), color_active if active_direction=='right' else color_idle, base_thickness + (1 if active_direction=='right' else 0), tipLength=0.5)

def fingertip_pixel(hand_landmarks, width, height):
    if not hand_landmarks:
        return None
    tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
    x_px = int(tip.x * width)
    y_px = int(tip.y * height)
    return (x_px, y_px)

def point_in_circle(px, py, cx, cy, r):
    dx = px - cx
    dy = py - cy
    return (dx * dx + dy * dy) <= (r * r)

def direction_from_point(px, py, centers, radius):
    for direction, (cx, cy) in centers.items():
        if point_in_circle(px, py, cx, cy, radius):
            return direction
    return None

def get_hand_direction(hand_landmarks, width, height, centers, radius):
    fp = fingertip_pixel(hand_landmarks, width, height)
    if fp is None:
        return None
    px, py = fp
    return direction_from_point(px, py, centers, radius)

def handle_restart(event):
    game.restart()

game.window.bind('<r>', handle_restart)

with mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5) as hands:

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.flip(frame, 1)

        h, w = frame.shape[:2]
        centers, radius = compute_overlay_geometry(w, h)

        # Determine active direction for highlight (if hand will be detected below this remains None)
        active_direction = None

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        results = hands.process(frame_rgb)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Draw landmarks for feedback
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                # Compute fingertip and direction by circular regions
                new_direction = get_hand_direction(hand_landmarks, w, h, centers, radius)
                if new_direction:
                    active_direction = new_direction
                    game.change_direction(new_direction)

                # Visualize fingertip point
                fp = fingertip_pixel(hand_landmarks, w, h)
                if fp is not None:
                    cv2.circle(frame, fp, 6, (0, 255, 255), -1)

        # Draw the direction pad overlay (after possibly setting active_direction)
        draw_direction_pad(frame, centers, radius, active_direction)

        cv2.putText(frame, f'Direction: {game.direction}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

        # Position windows once when frame size is known
        position_windows(w, h)

        # Show restart overlay if game is over
        if getattr(game, 'is_game_over', False):
            draw_restart_overlay(frame)

        cv2.imshow(WINDOW_NAME, frame)

        game.window.update_idletasks()
        game.window.update()

        key = cv2.waitKey(1) & 0xFF
        if key == ord('r'):
            game.restart()
            position_windows(w, h)
        if key == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
