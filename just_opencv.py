import cv2
import mediapipe as mp
from snake_game import start_game

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

game = start_game()

def get_hand_direction(hand_landmarks):
    if hand_landmarks:
        x = 1.0 -hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].x
        y = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y
        
        if x < 0.3:
            return 'right'  
        elif x > 0.7:
            return 'left'   
        elif y < 0.3:
            return 'up'     
        elif y > 0.7:
            return 'down'   
    return None

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
        frame = cv2.flip(frame,1)
        
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        results = hands.process(frame_rgb)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                new_direction = get_hand_direction(hand_landmarks)
                if new_direction:
                    game.change_direction(new_direction)
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        cv2.putText(frame, f'Direction: {game.direction}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

        cv2.imshow('Hand Tracking', frame)

        game.window.update_idletasks()
        game.window.update()

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
