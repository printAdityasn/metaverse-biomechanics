import cv2
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from cvzone.PoseModule import PoseDetector

class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Void BioTracker")
        self.geometry("600x200")
        self.is_paused = False

        self.create_widgets()

    def create_widgets(self):
        # Create the main frame for the application
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Create a label for the title
        self.title_label = ttk.Label(self.main_frame, text="Void BioTracker", font=("Arial", 20, "bold"))
        self.title_label.grid(row=0, column=0, columnspan=4, padx=10, pady=10)

        # Create a frame for the live camera test
        self.live_camera_frame = ttk.LabelFrame(self.main_frame, text="Live Camera Test")
        self.live_camera_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        # Create a button to start the live camera
        self.live_camera_button = ttk.Button(self.live_camera_frame, text="Start Wireframing Camera", command=self.on_click1)
        self.live_camera_button.pack(padx=10, pady=10)

        # Create a frame for the prerecorded video test
        self.prerecorded_video_frame = ttk.LabelFrame(self.main_frame, text="Prerecorded Video Test")
        self.prerecorded_video_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

        # Create a label and entry for selecting video file
        self.video_name_label = ttk.Label(self.prerecorded_video_frame, text="Video Path:")
        self.video_name_label.grid(row=0, column=0, padx=5, pady=5)
        self.video_name_entry = ttk.Entry(self.prerecorded_video_frame, width=30)
        self.video_name_entry.grid(row=0, column=1, padx=5, pady=5)

        # Create a browse button to select a video file
        self.browse_button = ttk.Button(self.prerecorded_video_frame, text="Browse", command=self.browse_video)
        self.browse_button.grid(row=0, column=2, padx=5, pady=5)

        # Create a frame to hold the sliders
        self.slider_frame = ttk.Frame(self.prerecorded_video_frame)
        self.slider_frame.grid(row=1, column=0, columnspan=3, padx=5, pady=5)

        # Create sliders for brightness, saturation, and whites
        self.create_slider("Brightness", 10, 50, 10, 1, 0)
        self.create_slider("Saturation", 100, 200, 100, 1, 1)
        self.create_slider("Whites", 100, 200, 100, 1, 2)

        # Create a button to show wireframe output
        self.show_wireframe_output_button = ttk.Button(self.prerecorded_video_frame, text="Show Wireframe Output", command=self.on_click2)
        self.show_wireframe_output_button.grid(row=2, column=0, columnspan=3, padx=5, pady=5)

    def create_slider(self, label_text, min_val, max_val, default_val, resolution, row):
        # Create a label for the slider
        label = ttk.Label(self.slider_frame, text=label_text)
        label.grid(row=row, column=0, padx=5, pady=5)

        # Create a slider
        slider = ttk.Scale(self.slider_frame, from_=min_val, to=max_val, orient="horizontal", length=200, value=default_val, command=self.on_slider_change, resolution=resolution)
        slider.grid(row=row, column=1, padx=5, pady=5)

    def on_slider_change(self, value):
        pass

    def on_click1(self):
        # Function to start the live camera
        detector = PoseDetector()
        cap = cv2.VideoCapture(0) 
        while True:
            success, img = cap.read()
            img = detector.findPose(img)
            cv2.imshow("Live Camera Test", img)
            c = cv2.waitKey(1)
            if c == 27:
                break
        cap.release()
        cv2.destroyAllWindows()

    def on_click2(self):
        # Function to start the prerecorded video test
        video_name1 = self.video_name_entry.get()
        if not video_name1:
            messagebox.showinfo("Error", "Please select a video :D")
            return
        detector = PoseDetector()
        cap = cv2.VideoCapture(video_name1)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        desired_fps = 60

        # Calculate the frame rate conversion factor
        fps_conversion_factor = desired_fps / cap.get(cv2.CAP_PROP_FPS)

        # Define the codec and create VideoWriter object
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter('output.avi', fourcc, desired_fps, (int(cap.get(3)), int(cap.get(4))))

        current_frame = 0
        prev_frame = None
        is_playing = True  # Variable to track play/pause state

        cv2.namedWindow("Prerecorded Video Test")

        def on_trackbar(pos):
            nonlocal current_frame
            current_frame = pos
            cap.set(cv2.CAP_PROP_POS_FRAMES, current_frame)

        cv2.createTrackbar("Position", "Prerecorded Video Test", 0, total_frames - 1, on_trackbar)

        while True:
            if is_playing:
                success, img = cap.read()
                if success:
                    img = detector.findPose(img)

                    # Get slider values for brightness, saturation, and white balance
                    brightness = cv2.getTrackbarPos("Brightness", "Prerecorded Video Test")
                    saturation = cv2.getTrackbarPos("Saturation", "Prerecorded Video Test") / 100.0
                    whites = cv2.getTrackbarPos("Whites", "Prerecorded Video Test") / 100.0

                    # Adjust brightness, saturation, and white balance
                    img = cv2.convertScaleAbs(img, alpha=1.0, beta=brightness)
                    img = cv2.convertScaleAbs(img, alpha=saturation, beta=whites)

                    if prev_frame is not None:
                        # Interpolation to increase frame rate
                        interpolated_frames = int(fps_conversion_factor)
                        for _ in range(interpolated_frames):
                            interpolated_frame = cv2.addWeighted(prev_frame, 0.3, img, 0.7, 0)  # Adjust the weights for a more popping effect
                            out.write(interpolated_frame)
                    out.write(img)
                    prev_frame = img

                    cv2.imshow("Prerecorded Video Test", img)
                    current_frame = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
                    cv2
