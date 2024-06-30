import cv2
import os
import tkinter as tk
from PIL import Image, ImageTk
from cvzone.PoseModule import PoseDetector

# Define a function to check if a point (x, y) is inside a rectangular region
def is_inside_rect(point, rect):
    x1, y1, x2, y2 = rect
    return x1 <= point[0] <= x2 and y1 <= point[1] <= y2

# Initialize video capture from the camera
cap = cv2.VideoCapture(0)  # Use the default camera (change to 1, 2, etc. for other cameras)
detector = PoseDetector()

# Paths for shirts and buttons
shirtFolderPath = "C:/xampp/htdocs/Virtual Try-on for Clothing_2/Resources/Shirts"
buttonPath = "C:/xampp/htdocs/Virtual Try-on for Clothing_2/Resources/button.png"

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
clothing_options = [
    {"name": "Shirt 1", "image_path": "C:/xampp/htdocs/Virtual Try-on for Clothing_2/Resources/Shirts/shirt1.png"},
    {"name": "Shirt 2", "image_path": "C:/xampp/htdocs/Virtual Try-on for Clothing_2/Resources/Shirts/shirt2.png"},
]

# Create a frame for clothing buttons
clothing_frame = tk.Frame(root)
clothing_frame.pack()

# Function to overlay clothing on the user's image
def overlay_clothing(clothing_image_path):
    global img  # Access the global user's image

    # Load the selected clothing image
    clothing_img = cv2.imread(clothing_image_path, cv2.IMREAD_UNCHANGED)

    # Resize the clothing image to match the user's dimensions (e.g., torso size)
    # You may need to adjust this resizing logic based on your specific use case
    desired_width = 100  # Adjust this as needed
    desired_height = 100  # Adjust this as needed
    clothing_img = cv2.resize(clothing_img, (desired_width, desired_height))

    # Calculate the position to overlay the clothing (e.g., on the user's torso)
    # You may need to adjust the position calculation based on your specific use case
    x_position = 100  # Adjust this as needed
    y_position = 100  # Adjust this as needed

    # Overlay the clothing on the user's image
    for y in range(clothing_img.shape[0]):
        for x in range(clothing_img.shape[1]):
            if clothing_img[y, x][3] > 0:  # Check alpha channel
                img_y = y_position + y
                img_x = x_position + x
                if 0 <= img_y < img.shape[0] and 0 <= img_x < img.shape[1]:
                    img[img_y, img_x, :] = clothing_img[y, x, :3]

# Function to select the next clothing item
def next_clothing():
    global selected_clothing_index
    selected_clothing_index = (selected_clothing_index + 1) % len(clothing_options)
    selected_clothing_name = clothing_options[selected_clothing_index]["name"]  # Get the name of the selected clothing
    select_clothing(selected_clothing_name)  # Pass the clothing name to select_clothing

# Function to select the previous clothing item
def prev_clothing():
    global selected_clothing_index
    selected_clothing_index = (selected_clothing_index - 1) % len(clothing_options)
    selected_clothing_name = clothing_options[selected_clothing_index]["name"]  # Get the name of the selected clothing
    select_clothing(selected_clothing_name)  # Pass the clothing name to select_clothing

# Function to handle clothing selection
def select_clothing(clothing_image_path):
    try_on_clothing(clothing_image_path)

# Function to try on the selected clothing
def try_on_clothing(clothing_image_path):
    global img
    overlay_clothing(clothing_image_path)
    cv2.imshow("Try On", img)

# Create a function to display the clothing selection screen
def show_clothing_selection():
    root.deiconify()

# Create buttons for each clothing option with images
for clothing in clothing_options:
    image_path = clothing["image_path"]
    image = Image.open(image_path)
    image = image.resize((100, 100), Image.LANCZOS)  # Resize the image to a suitable size
    tk_image = ImageTk.PhotoImage(image=image)

    button = tk.Button(
        clothing_frame,
        image=tk_image,
        text=clothing["name"],
        compound=tk.TOP,  # Display image above the text
        command=lambda path=image_path: select_clothing(path),
    )
    button.image = tk_image  # Store a reference to the image to prevent it from being garbage collected
    button.pack(side=tk.LEFT, padx=10, pady=10)

# Create "Next" and "Previous" buttons
next_button = tk.Button(root, text="Next", command=next_clothing)
next_button.pack()
prev_button = tk.Button(root, text="Previous", command=prev_clothing)
prev_button.pack()

def try_on_button_click():
    show_clothing_selection()  # Show the clothing selection UI
    try_on_clothing(clothing_options[selected_clothing_index]["image_path"])  # Automatically try on the initial clothing

# Create a "Try On" button to trigger the try-on functionality
try_on_button = tk.Button(root, text="Try On", command=try_on_button_click)
try_on_button.pack()

while True:
    success, frame = cap.read()
    # Check if video capture was successful
    if not success:
        print("Video capture failed. Exiting.")
        break

    img = frame.copy()  # Copy the frame to img
    # Rest of your code...

    img = cv2.flip(img, 1)
    img = detector.findPose(img)
    lmList, bboxInfo = detector.findPosition(img, bboxWithHands=False, draw=False)

    if lmList:
        lm11 = lmList[11][1:3]
        lm12 = lmList[12][1:3]
        torso_center = ((lm11[0] + lm12[0]) // 2, (lm11[1] + lm12[1]) // 2)

        overlay_pos_right = (1074, 293)
        overlay_pos_left = (72, 293)

        if 0 <= imageNumber < len(listShirts):
            imgShirtPath = os.path.join(shirtFolderPath, listShirts[imageNumber])
            imgShirt = cv2.imread(imgShirtPath, cv2.IMREAD_UNCHANGED)

            # Calculate the desired width of the shirt based on body measurements
            desired_shirt_width = int((lm11[0] - lm12[0]) * fixedRatio)

            # Resize the shirt image while maintaining the aspect ratio
            aspect_ratio = imgShirt.shape[1] / imgShirt.shape[0]
            imgShirt_resized = cv2.resize(imgShirt, (desired_shirt_width, int(desired_shirt_width / aspect_ratio)))

            # Calculate the position to place the shirt
            shirt_x = int(torso_center[0] - imgShirt_resized.shape[1] / 2)
            shirt_y = int(torso_center[1] - imgShirt_resized.shape[0] / 7)

            # Overlay the resized shirt image onto the user's image
            for y in range(imgShirt_resized.shape[0]):
                for x in range(imgShirt_resized.shape[1]):
                    if imgShirt_resized[y, x][3] > 0:  # Check alpha channel
                        img_y = shirt_y + y
                        img_x = shirt_x + x
                        if 0 <= img_y < img.shape[0] and 0 <= img_x < img.shape[1]:
                            img[img_y, img_x, :] = imgShirt_resized[y, x, :3]

        # Get the coordinates of the button areas
        button_rect_right = (overlay_pos_right[0], overlay_pos_right[1], overlay_pos_right[0] + buttonWidth, overlay_pos_right[1] + buttonHeight)
        button_rect_left = (overlay_pos_left[0], overlay_pos_left[1], overlay_pos_left[0] + buttonWidth, overlay_pos_left[1] + buttonHeight)

        # Check if the user clicked on the buttons
        if is_inside_rect(lmList[8][1:3], button_rect_right):
            # Handle right button click event here
            if imageNumber < len(listShirts) - 1:
                imageNumber += 1
                select_clothing(clothing_options[selected_clothing_index]["name"])  # Update the clothing overlay when changing clothing

        elif is_inside_rect(lmList[8][1:3], button_rect_left):
            # Handle left button click event here
            if imageNumber > 0:
                imageNumber -= 1
                select_clothing(clothing_options[selected_clothing_index]["name"])  # Update the clothing overlay when changing clothing

    cv2.imshow("Image", img)

    # Set window properties for full screen
    cv2.namedWindow("Image", cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty("Image", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    if cv2.waitKey(1) == 27:  # Press Esc to exit
        break

cap.release()
cv2.destroyAllWindows()
root.mainloop()
