import face_recognition
import cv2
import shutil
import os
from datetime import datetime
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import mysql.connector
import requests
from io import BytesIO
import threading


var = None

# Function to capture multiple images for a new user
def capture_images(name):
    capture = cv2.VideoCapture(0)
    capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # Adjust width
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    count = 0

    # Create a directory for the new user if it doesn't exist
    user_dir = os.path.join(known_faces_dir, name)
    os.makedirs(user_dir, exist_ok=True)

    while count < 3:  # Capture 3 images
        ret, frame = capture.read()
        if not ret:
            raise ValueError("Camera read failed. Check camera connection or configuration.")

        cv2.imshow('Capture Images', frame)
        if cv2.waitKey(1) & 0xFF == ord('c'):  # Press 'c' to capture an image
            img_name = os.path.join(user_dir, f'{name}_{count}.jpg')
            cv2.imwrite(img_name, frame)
            print(f"Image {count+1} captured for {name}")
            count += 1

    capture.release()
    cv2.destroyAllWindows()
    
# Function to select images from local storage
def select_images(name):
    root = tk.Tk()
    root.withdraw()

    # Let the user choose 3 images
    file_paths = filedialog.askopenfilenames(title="Select 3 images", filetypes=[("Image files", ".jpg;.png")])

    # Create a directory for the new user if it doesn't exist
    user_dir = os.path.join(known_faces_dir, name)
    os.makedirs(user_dir, exist_ok=True)

    count = 0
    for file_path in file_paths:
        img_name = os.path.join(user_dir, f'{name}_{count}.jpg')
        # Copy the selected image to the user's directory using shutil.copy
        shutil.copy(file_path, img_name)
        print(f"Image {count+1} selected for {name}")
        count += 1
        
known_faces_dir = "C:\\Users\\RUDRA\\OneDrive\\Desktop\\face_recognotion_system\\known_faces"
# Function to handle user registration
def register_user():
    global var
    new_user_name = entry.get()
    user_dir = os.path.join(known_faces_dir, new_user_name)
    label_result.place(x=15, y=370)

    if os.path.exists(user_dir):
        label_result.config(text="User already exists. Proceeding to face recognition.")
    else:
        registration_method = var.get()

        if registration_method == 1:
            label_result.config(text="User not found. Capturing images for the new user.")
            capture_images(new_user_name)
        elif registration_method == 2:
            label_result.config(text="User not found. Selecting images from local storage for the new user.")
            select_images(new_user_name)
        else:
            label_result.config(text="Invalid choice for registration method. Exiting.")

def delete_user_directory():
    name = entry.get().strip()  # Get and remove leading/trailing spaces

    if not name:
        label_result.config(text="Please enter a valid user name.")
        label_result.place(x=15, y=350)
        return

    user_dir = os.path.join(known_faces_dir, name)

    # Check if the user directory exists
    if os.path.exists(user_dir):
        # Remove the entire user directory
        shutil.rmtree(user_dir)
        print(f"User directory deleted for {name}")
        label_result.config(text="User directory deleted.")
        label_result.place(x=15, y=350)
    else:
        print(f"No directory found for {name}")
        label_result.config(text="User directory not found.")
        label_result.place(x=15, y=350)        



def run_face_recognition_thread():

    # Function to run face recognition
    known_faces_dir = "C:\\Users\\RUDRA\\OneDrive\\Desktop\\face_recognotion_system\\known_faces"

    known_face_encodings = []
    known_face_names = []

    for root, dirs, files in os.walk(known_faces_dir):
        for file in files:
            if file.endswith("jpg") or file.endswith("png"):
                path = os.path.join(root, file)
                face_image = face_recognition.load_image_file(path)
                face_encoding = face_recognition.face_encodings(face_image)[0]  # Assuming one face per image
                known_face_encodings.append(face_encoding)
                name = os.path.basename(root).replace(" ", "-").lower()
                known_face_names.append(name)

    video_cap = cv2.VideoCapture(0)
    video_cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)  # Adjust width
    video_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    # Connect to MySQL database
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Vgtr123!",
        database="attendance"
    )

    cursor = conn.cursor()

    while True:
        try:
            ret, video_data = video_cap.read()
            if not ret:
                raise ValueError("Camera read failed. Check camera connection or configuration.")
            
            small_frame = cv2.resize(video_data, (0, 0), fx=0.25, fy=0.25)
            rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            for face_encoding, face_location in zip(face_encodings, face_locations):
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                name = "Unknown"

                if True in matches:
                    first_match_index = matches.index(True)
                    name = known_face_names[first_match_index]
                    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    date, time = current_time.split()

                try:
                    # Your existing code to insert data into the database
                        insert_query = "INSERT INTO face_recognition_data (name, date, time) VALUES (%s, %s, %s)"
                        cursor.execute(insert_query, (name, date, time))
                        conn.commit()

                except mysql.connector.IntegrityError as e:
                    # IntegrityError will be raised if there's a uniqueness violation
                        print(f"Data insertion failed: {e}")
                    # Handle the case where duplicate data is detected (e.g., display a message or take appropriate action)


                top, right, bottom, left = face_location
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4

                cv2.rectangle(video_data, (left, top), (right, bottom), (0, 0, 0), 2)
                # Change the font style, color, and size here
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 1.0
                font_thickness = 2
                text_color = (255, 0, 0)  # Change the text color (BGR format)

                cv2.putText(video_data, name, (left + 6, bottom - 6), font, font_scale, text_color, font_thickness)
                # cv2.putText(video_data, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 0), 1)

            cv2.imshow("video_live", video_data)
            if cv2.waitKey(10) == ord("a"):  # Press 'a' to exit the loop
                break

        except Exception as e:
            print(f"Error: {str(e)}")
            break

    cursor.close()
    video_cap.release()
    cv2.destroyAllWindows()

def start_face_recognition():
    face_recognition_thread = threading.Thread(target=run_face_recognition_thread)
    face_recognition_thread.start()    

# Create the main registration window
main_window = tk.Tk()
main_window.title("Student Registration")

var = tk.IntVar()

# Load background image from URL
background_url = "https://learn.g2.com/hubfs/G2CM_FI454_Learn_Article_Images_%5BFacial_recognition%5D_V1a-1.png"
response = requests.get(background_url)
background_image = Image.open(BytesIO(response.content))
background_photo = ImageTk.PhotoImage(background_image)

# Set background image
background_label = tk.Label(main_window, image=background_photo)
background_label.place(x=0, y=0, relwidth=1, relheight=1)


# Entry widget for user name
entry_label = tk.Label(main_window, text="Enter your name:", font=("Arial", 20))
entry_label.place(x=15, y=20)  # Set x and y coordinates

entry = tk.Entry(main_window)
entry.place(x=17, y=65)  # Set x and y coordinates

# Radio buttons for registration method
radio_label = tk.Label(main_window, text="Choose registration method:", font=("Arial", 20))
radio_label.place(x=15, y=100)  # Set x and y coordinates

radio_capture = tk.Radiobutton(main_window, text="Capture Images", variable=var, value=1)
radio_capture.place(x=15, y=150)  # Set x and y coordinates

radio_select = tk.Radiobutton(main_window, text="Select Images from Local Storage", variable=var, value=2)
radio_select.place(x=15, y=200)  # Set x and y coordinates

# Button to delete the entire user directory
delete_directory_button = tk.Button(main_window, text="Delete User Directory", command=delete_user_directory)
delete_directory_button.place(x=15, y=250)  # Set x and y coordinates

# Button to initiate registration
register_button = tk.Button(main_window, text="Submit", command=lambda: [register_user(), start_face_recognition()])
register_button.place(x=15, y=300)  # Set x and y coordinates

# Label to display the result
label_result = tk.Label(main_window, text="")
label_result.place(x=15, y=370)

main_window.geometry("1920x1080")  # Set the desired width and height

main_window.mainloop()    