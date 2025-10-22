# Gesture-Controlled Snake Game

This project reimagines the classic Snake game by introducing a modern, intuitive control mechanism: hand gestures detected via a webcam. It seamlessly integrates a traditional GUI-based game with real-time computer vision to offer a unique interactive experience.

## Project Overview

The application consists of two main components working in tandem:
1.  A standard Snake game implemented using Python's Tkinter library.
2.  A hand tracking and gesture recognition system built with OpenCV and MediaPipe, which translates hand movements into game commands.

The game and the camera feed are displayed in separate, dynamically positioned windows, allowing users to control the snake by simply pointing their index finger towards directional zones shown on the camera feed.

## Topics Used

### 1. Python

*   **Explanation**: Python serves as the primary programming language for the entire project, leveraging its extensive ecosystem of libraries for GUI development, computer vision, and general-purpose programming.
*   **Theoretical Usage**: Python's readability and rich libraries enable rapid development and integration of diverse functionalities, from game logic to real-time image processing.

### 2. Tkinter (GUI Framework)

*   **Explanation**: Tkinter is Python's standard library for creating graphical user interfaces. In this project, it's used to construct the visual elements of the Snake game, including the main game window, the canvas where the snake and food are drawn, and the score display. It also manages the game's internal state and timing through its event loop.
*   **Theoretical Usage**: Tkinter provides fundamental widgets like `Tk` (the main application window), `Canvas` (a versatile drawing area for custom graphics), and `Label` (for displaying text like the score). The game logic updates these widgets, and `window.after()` is crucial for scheduling recurring game updates, forming the core of the game's animation loop.
*   **Core Logic Snippet (`snake_game.py`):**
    ```python
    # Initialization of main window, canvas, and score label
    self.window = Tk()
    self.canvas = Canvas(self.window, bg=BACKGROUND_COLOR, height=GAME_HEIGHT, width=GAME_WIDTH)
    self.canvas.pack()
    self.label = Label(self.window, text="Score:{}".format(self.score), font=('consolas', 40))
    self.label.pack()

    # Scheduling the first game turn, initiating the game loop
    self.window.after(SPEED, self.next_turn)

    # Example of drawing game elements on the canvas
    square = self.canvas.create_rectangle(x, y, x + SPACE_SIZE, y + SPACE_SIZE, fill=SNAKE_COLOR)
    self.canvas.create_oval(fx, fy, fx + SPACE_SIZE, fy + SPACE_SIZE, fill=FOOD_COLOR, tag="food")
    ```

### 3. OpenCV (Computer Vision Library)

*   **Explanation**: OpenCV (Open Source Computer Vision Library) is a powerful library for real-time computer vision tasks. Here, it's primarily used to access the computer's webcam, capture video frames, display them in a separate window, and perform basic image manipulations like flipping the frame and drawing overlays (e.g., the directional pad). It also handles keyboard and mouse input for the OpenCV window.
*   **Theoretical Usage**: OpenCV's `cv2.VideoCapture` class provides an interface to camera devices. Video frames are read iteratively in a loop, processed (e.g., color conversion, flipping), and then displayed using `cv2.imshow`. Drawing functions like `cv2.circle`, `cv2.rectangle`, and `cv2.putText` are used to provide visual feedback and interactive UI elements directly on the camera feed.
*   **Core Logic Snippet (`just_opencv.py`):**
    ```python
    import cv2

    cap = cv2.VideoCapture(0) # Initialize webcam (0 for default camera)
    cv2.namedWindow('Hand Tracking', cv2.WINDOW_NORMAL) # Create a resizable window

    while cap.isOpened():
        ret, frame = cap.read() # Read a frame from the camera
        if not ret: break
        frame = cv2.flip(frame, 1) # Flip frame horizontally for mirror effect
        # ... further frame processing (e.g., hand detection, drawing overlays) ...
        cv2.imshow('Hand Tracking', frame) # Display the processed frame
        key = cv2.waitKey(1) & 0xFF # Wait for a key press (1ms delay)
        if key == ord('q'): # Check for 'q' to quit
            break
    ```

### 4. MediaPipe Hands (Hand Landmark Detection)

*   **Explanation**: MediaPipe Hands is a Google-developed machine learning solution that provides real-time, high-fidelity 3D hand landmark detection. It takes an image as input and outputs 21 3D coordinates (landmarks) for each detected hand, representing key points like fingertips, knuckles, and the wrist. In this project, it's crucial for identifying the precise pixel position of the index fingertip, which is then used for gesture control.
*   **Theoretical Usage**: The `mp.solutions.hands.Hands` object is initialized to configure the hand detection model. It processes an RGB image, and if hands are detected, it returns a `multi_hand_landmarks` object containing the normalized coordinates (ranging from 0 to 1) of each landmark. These normalized coordinates are then scaled to the actual pixel dimensions of the video frame to get their absolute positions.
*   **Core Logic Snippet (`just_opencv.py`):**
    ```python
    import mediapipe as mp
    mp_hands = mp.solutions.hands # Import MediaPipe Hands module

    with mp_hands.Hands(
        static_image_mode=False, max_num_hands=1,
        min_detection_confidence=0.5, min_tracking_confidence=0.5) as hands:

        while cap.isOpened():
            # ... frame capture ...
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) # Convert BGR frame to RGB
            results = hands.process(frame_rgb) # Process the frame for hand landmarks

            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    # Access the index fingertip landmark
                    tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
                    # Scale normalized coordinates to pixel coordinates
                    x_px = int(tip.x * w)
                    y_px = int(tip.y * h)
                    # ... use x_px, y_px for gesture detection ...
    ```

### 5. Gesture Recognition Logic

*   **Explanation**: This is the core mechanism that translates the detected hand movements into game commands. The OpenCV window displays an overlay with four circular regions, each representing a direction (up, down, left, right). The project continuously monitors if the user's index fingertip (detected by MediaPipe) falls within one of these active regions. If it does, the corresponding direction command is sent to the Snake game.
*   **Theoretical Usage**: Predefined circular zones are established on the camera feed, acting as virtual buttons. The pixel coordinates of the index fingertip are calculated in real-time. A simple geometric check (`point_in_circle`) determines if the fingertip's current position is inside any of these direction zones. This allows for intuitive, touch-like interaction with the game without physical contact.
*   **Core Logic Snippet (`just_opencv.py`):**
    ```python
    def compute_overlay_geometry(width, height):
        # Defines center coordinates and radius for 'up', 'down', 'left', 'right' zones
        radius = int(min(width, height) * 0.10)
        centers = {
            'up':    (int(width * 0.50), int(height * 0.20)),
            'down':  (int(width * 0.50), int(height * 0.80)),
            'left':  (int(width * 0.20), int(height * 0.50)),
            'right': (int(width * 0.80), int(height * 0.50)),
        }
        return centers, radius

    def point_in_circle(px, py, cx, cy, r):
        # Checks if point (px, py) is within a circle centered at (cx, cy) with radius r
        return (px - cx)**2 + (py - cy)**2 <= r**2

    def get_hand_direction(hand_landmarks, width, height, centers, radius):
        fp = fingertip_pixel(hand_landmarks, width, height) # Get index fingertip pixel coordinates
        if fp:
            px, py = fp
            for direction, (cx, cy) in centers.items():
                if point_in_circle(px, py, cx, cy, radius):
                    return direction # Return the detected direction
        return None
    ```

### 6. Game Loop and Event Handling

*   **Explanation**: The project employs a dual-loop architecture: one for the Tkinter game and one for the OpenCV camera feed. The Tkinter loop (`game.window.after`) is responsible for advancing the game state (moving the snake, checking for collisions, updating score) at regular intervals. The OpenCV loop continuously captures and processes video frames. When a gesture is recognized in the OpenCV loop, it directly calls a method in the `SnakeGame` instance (`game.change_direction()`) to update the snake's intended movement. Keyboard events (like 'r' for restart, 'q' for quit) are handled by both loops for responsiveness.
*   **Theoretical Usage**: This dual-loop design allows for independent management of the game's visual and logical updates and the real-time camera processing. Communication between the two is achieved by having the OpenCV loop directly interact with the `SnakeGame` object, effectively bridging the two frameworks. Tkinter's `update()` and `update_idletasks()` methods are called within the OpenCV loop to ensure the Tkinter window remains responsive.
*   **Core Logic Snippet (`snake_game.py` and `just_opencv.py`):**
    ```python
    # Tkinter game loop scheduling (from snake_game.py)
    class SnakeGame:
        # ...
        def next_turn(self):
            # ... game state update logic (move snake, check collisions, etc.) ...
            self.window.after(SPEED, self.next_turn) # Schedule the next game turn

    # Interaction within the OpenCV processing loop (from just_opencv.py)
    while cap.isOpened():
        # ... frame capture and hand detection ...
        new_direction = get_hand_direction(hand_landmarks, w, h, centers, radius)
        if new_direction:
            game.change_direction(new_direction) # Call Tkinter game method to change direction

        # Ensure Tkinter window updates
        game.window.update_idletasks()
        game.window.update()
    ```

### 7. Window Management

*   **Explanation**: To provide a seamless user experience, the project dynamically positions both the Tkinter game window and the OpenCV camera feed window on the screen. It attempts to place them side-by-side, typically with the game on the left and the camera feed on the right, adjusting for screen size and maintaining a clean layout.
*   **Theoretical Usage**: Tkinter's `winfo_screenwidth()` and `winfo_screenheight()` methods are used to retrieve the dimensions of the user's screen. `game.window.geometry()` is then used to set the position and size of the Tkinter window. Similarly, OpenCV's `cv2.moveWindow()` and `cv2.resizeWindow()` functions are employed to control the position and size of its display window. This coordinated positioning enhances usability by presenting both interactive elements clearly.
*   **Core Logic Snippet (`just_opencv.py`):**
    ```python
    def position_windows(frame_width, frame_height):
        screen_w = game.window.winfo_screenwidth()
        screen_h = game.window.winfo_screenheight()

        # Calculate optimal positions for left (Tkinter) and right (OpenCV) windows
        left_x = 50
        left_y = 50
        right_x = min(left_x + int(screen_w * 0.5), max(0, screen_w - frame_width - 50))
        right_y = left_y

        # Apply calculated positions to both windows
        gw = game.window.winfo_width()
        gh = game.window.winfo_height()
        game.window.geometry(f"{gw}x{gh}+{left_x}+{left_y}") # Position Tkinter window
        cv2.resizeWindow(WINDOW_NAME, frame_width, frame_height)
        cv2.moveWindow(WINDOW_NAME, right_x, right_y) # Position OpenCV window
    ```

## How to Run

1.  **Prerequisites**: Ensure you have Python installed.
2.  **Install Dependencies**:
    ```bash
    pip install opencv-python mediapipe
    ```
3.  **Run the script**:
    ```bash
    python just_opencv.py
    ```
    This will launch both the Snake game window and the webcam feed window.

## Future Goals

*   Implement more complex gestures (e.g., pinch to pause, swipe to change speed).
*   Add different game modes or levels to increase replayability.
*   Improve the UI/UX of the gesture control overlay for better clarity.
*   Package the application into an executable for easier distribution.```
