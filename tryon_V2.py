import cv2
import os
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
from cvzone.PoseModule import PoseDetector
import numpy as np

# Define a function to check if a point (x, y) is inside a rectangular region
def is_inside_rect(point, rect):
    x1, y1, x2, y2 = rect
    return x1 <= point[0] <= x2 and y1 <= point[1] <= y2

# Initialize video capture from the camera
cap = cv2.VideoCapture(0)  # Use the default camera (change to 1, 2, etc. for other cameras)
detector = PoseDetector()

# Paths for shirts and buttons
shirtFolderPath = "./Resources/Shirts"
buttonPath = "./Resources/button.png"

# Load button image and resize
buttonImg = cv2.imread(buttonPath, cv2.IMREAD_UNCHANGED)
buttonWidth = 100
buttonHeight = 100
imgButtonRight = cv2.resize(buttonImg, (buttonWidth, buttonHeight))

# Load shirt list and setup
listShirts = os.listdir(shirtFolderPath)
fixedRatio = 262 / 165
shirtRatioHeightWidth = 481 / 440
imageNumber = 0
selectionSpeed = 10

# Create a main application window
root = tk.Tk()
root.title("Virtual Clothing Try-On")

# Create a variable to store the selected clothing choice
selected_clothing_index = 0
selected_clothing_image_path = None

clothing_options = [
    {"name": "Shirt 1", "image_path": "./Resources/Shirts/shirt1.png"},
    {"name": "Shirt 2", "image_path": "./Resources/Shirts/shirt2.png"},
]

# Create a frame for clothing buttons
clothing_frame = tk.Frame(root)
clothing_frame.pack()

# Function to overlay clothing on the user's image
def overlay_clothing(img, clothing_image_path):
    clothing_img = cv2.imread(clothing_image_path, cv2.IMREAD_UNCHANGED)

    desired_width = 200  # Adjust for the torso size
    desired_height = 300  # Adjust for the torso size
    clothing_img = cv2.resize(clothing_img, (desired_width, desired_height))

    x_position = 100  # Adjust the x-axis position
    y_position = 100  # Adjust the y-axis position

    try:
        aspect_ratio = clothing_img.shape[1] / clothing_img.shape[0]
        img_resized = cv2.resize(clothing_img, (desired_width, int(desired_width / aspect_ratio)))

        # Overlay the resized clothing image
        for y in range(img_resized.shape[0]):
            for x in range(img_resized.shape[1]):
                if img_resized[y, x][3] > 0:  # Check alpha channel for transparency
                    img_y = y_position + y
                    img_x = x_position + x
                    if 0 <= img_y < img.shape[0] and 0 <= img_x < img.shape[1]:
                        img[img_y, img_x, :] = img_resized[y, x, :3]
    except Exception as e:
        print(f"Error overlaying clothing image: {e}")

# Function to select the next clothing item
def next_clothing():
    global selected_clothing_index
    selected_clothing_index = (selected_clothing_index + 1) % len(clothing_options)
    select_clothing(clothing_options[selected_clothing_index]["image_path"])

# Function to select the previous clothing item
def prev_clothing():
    global selected_clothing_index
    selected_clothing_index = (selected_clothing_index - 1) % len(clothing_options)
    select_clothing(clothing_options[selected_clothing_index]["image_path"])

# Function to handle clothing selection
def select_clothing(clothing_image_path):
    global selected_clothing_image_path
    selected_clothing_image_path = clothing_image_path
    start_try_on()

# Function to try on the selected clothing
def try_on_clothing(img):
    if selected_clothing_image_path:
        overlay_clothing(img, selected_clothing_image_path)
    cv2.imshow("Try On", img)

# Function to upload a custom shirt
def upload_custom_shirt():
    global selected_clothing_image_path
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg")])
    if file_path:
        selected_clothing_image_path = file_path
        start_try_on()

# Create buttons for each clothing option with images
for clothing in clothing_options:
    image_path = clothing["image_path"]
    image = Image.open(image_path)
    image = image.resize((100, 100), Image.LANCZOS)
    tk_image = ImageTk.PhotoImage(image=image)

    button = tk.Button(
        clothing_frame,
        image=tk_image,
        text=clothing["name"],
        compound=tk.TOP,
        command=lambda path=image_path: select_clothing(path),
    )
    button.image = tk_image  # Store reference to prevent garbage collection
    button.pack(side=tk.LEFT, padx=10, pady=10)

# Create "Next" and "Previous" buttons
next_button = tk.Button(root, text="Next", command=next_clothing)
next_button.pack()
prev_button = tk.Button(root, text="Previous", command=prev_clothing)
prev_button.pack()

# Create an "Upload" button
upload_button = tk.Button(root, text="Upload Custom Shirt", command=upload_custom_shirt)
upload_button.pack(pady=10)

def start_try_on():
    while True:
        success, frame = cap.read()
        if not success:
            print("Video capture failed. Exiting.")
            break

        img = frame.copy()
        img = cv2.flip(img, 1)
        img = detector.findPose(img)
        lmList, bboxInfo = detector.findPosition(img, bboxWithHands=False, draw=False)

        if lmList:
            try_on_clothing(img)
        else:
            cv2.imshow("Try On", img)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# Start the virtual try-on experience
root.mainloop()
