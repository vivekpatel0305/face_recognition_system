# Face Recognition System

This project is a Python-based face recognition system with a Tkinter GUI for registering and recognizing users. The system allows users to register by capturing images via webcam or by selecting images from local storage. It stores the face data and performs real-time face recognition using a webcam, recording recognized faces into a MySQL database.

## Features

- **User Registration**: 
  - Capture images directly from the webcam.
  - Select images from local storage for registration.
  
- **Face Recognition**: 
  - Recognize registered users in real-time through webcam input.
  - Automatically logs recognized users with date and time into a MySQL database.

- **User Directory Management**:
  - Delete an entire user’s directory and their associated images.

## Prerequisites

Before running the project, ensure you have the following dependencies installed:

- Python 3.x
- OpenCV
- Face Recognition Library
- Tkinter
- MySQL Connector for Python
- Requests
- PIL (Python Imaging Library)
- threading
- shutil

You can install the required packages using pip:

```bash
pip install opencv-python face-recognition mysql-connector-python pillow requests
```

### MySQL Database

Ensure you have MySQL installed and running. Create a database and table with the following structure:

```sql
CREATE DATABASE attendance;

USE attendance;

CREATE TABLE face_recognition_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    date DATE,
    time TIME
);
```

Update the MySQL connection details in the code:
```python
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="YOUR_PASSWORD",
    database="attendance"
)
```

## Project Structure

```bash
project/
│
├── face_recognition_system.py # Main Python code
└── known_faces/              # Directory where user images will be stored
```

## How to Run

1. **Clone the repository** or download the `face_recognition_system.py` script.
2. **Install the dependencies** listed in the prerequisites section.
3. **Run the script**:
   ```bash
   python face_recognition_system.py
   ```
4. **Register Users**:
   - Enter the user's name.
   - Choose the registration method (Capture Images or Select Images).
   - If capturing images, press the `c` key to capture an image.
5. **Start Face Recognition**: The face recognition thread will automatically start after registration. It will recognize users and log the data in the MySQL database.
6. **Delete Users**: Use the `Delete User Directory` button to remove a user and their data.

## Usage

- Press `a` during face recognition to exit the loop.
- Check the MySQL database for logged face recognition data.

## GUI Overview

- The GUI allows you to enter a name, choose a registration method, submit the data, and start the face recognition process.
- The system uses a background image loaded from a URL for the interface design.

## Issues and Error Handling

- If the camera is not detected, ensure that it is properly connected and configured.
- Handle potential MySQL errors such as duplicate entries with proper exception handling in the code.

## Future Improvements

- Add functionality for updating or modifying user images.
- Implement additional face recognition algorithms for better accuracy.
- Enhance the GUI design for a more user-friendly interface.
