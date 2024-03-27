import cv2
import numpy as np
import face_recognition
import os, sys
import math
import pickle
import re
import statistics
from random import choice
from tkinter import *

def popup_window():
    window = Tk()
    window.title("Saving a new face")
    window.geometry("200x200")

    disp_text = Label(window, text="Success", font=("Arial Bold", 25))
    disp_text.grid(column=0, row=0)

    input_text = Entry(window, width=10)
    input_text.grid(column=0, row=1)

    # Function to retrieve input and close window
    def handle_save():
        global user_input
        user_input = input_text.get()  # Get input text
        window.destroy()  # Close the window

    button = Button(window, text="Save", font=("Arial Bold", 12), bg="dark green", fg="white", command=handle_save)
    button.grid(column=0, row=2)

    window.mainloop()

    # Return the retrieved input, not using file_text (modify if needed)
    return user_input

def save_img(image):
    main_directory = os.path.dirname(os.path.realpath(__file__))
    download_folder = os.path.join(main_directory, "faces")
    inputted_name = popup_window()
    filename = f"{inputted_name}.jpg"
    filepath = os.path.join(download_folder, filename)
    try: 
        cv2.imwrite(filepath, image)
    except Exception as e:
        print("Error saving file:", e)
    return filename, filepath


# Main FR class
class FaceRecognition:
    face_locations = []
    face_encodings = []
    face_names = []
    known_face_names = []
    known_face_encodings = []
    process_current_frame = True
    name_list = []
    framecounter = 0
    filename_counter = 0
    

    def __init__(self):
        self.encode_faces()
    

    # Encode faces in directory "faces" and put them in "facial_encodings.pkl" if it doesnt exist
    def encode_faces(self):
        main_directory = os.path.dirname(os.path.realpath(__file__))
        faces_saved = os.path.join(main_directory, "facial_encodings.pkl")
        
        if not os.path.exists(faces_saved):
            for image in os.listdir("faces"):
                face_image = face_recognition.load_image_file(f"faces/{image}")
                face_encoding = face_recognition.face_encodings(face_image)[0]
            
            #exception handling if "faces" folder is empty
                try:
                    self.known_face_encodings.append(face_encoding)
                    print(f"Added image: {image}")
                except UnboundLocalError:
                    print("No item in directory 'faces'.")

            with open("facial_encodings.pkl", "wb") as f:
                pickle.dump(self.known_face_encodings, f)

        for image in os.listdir("faces"):
            try:
                self.known_face_names.append(image)
            except UnboundLocalError:
                print("No item in directory 'faces'.")
                
        print(self.known_face_names)

    # Main recognition function
    def run_recognition(self):
        main_directory = os.path.dirname(os.path.realpath(__file__))
        download_folder = os.path.join(main_directory, "faces")
        video_capture = cv2.VideoCapture(0)

        if not video_capture.isOpened():
            sys.exit("Video source not found...")

        # Opens the pickle file with the encodings
        with open("facial_encodings.pkl", "rb") as f:
            self.known_face_encodings = pickle.load(f)

        while True:
            ret, frame = video_capture.read()

            if self.process_current_frame:
                small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
                rgb_small_frame = small_frame[:, :, ::-1]

                self.face_locations = face_recognition.face_locations(rgb_small_frame)
                self.face_encodings = face_recognition.face_encodings(rgb_small_frame)
                self.face_names = []

                for face_encoding in self.face_encodings:
                    matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
                    name = "Unknown"

                    face_distaces = face_recognition.face_distance(self.known_face_encodings, face_encoding)
                    best_match_index = np.argmin(face_distaces)

                    if matches[best_match_index]:
                        name = self.known_face_names[best_match_index]

                    self.face_names.append(name)

                    if self.framecounter >= 19:
                        if statistics.multimode(self.name_list)[0] == "Unknown":
                            try:
                                self.framcounter = 0
                                new_name, filepath_new = save_img(frame)
                                cv2.destroyAllWindows()
                                self.known_face_names.append(new_name)
                                self.face_image = face_recognition.load_image_file(filepath_new)
                                face_location = face_recognition.face_locations(self.face_image)
                                encoding = face_recognition.face_encodings(self.face_image, face_location)[0]
                                #pickle_file_path = os.path.join(self.main_directory, "facial_encodings.pkl")
                                #with open(pickle_file_path, "rb") as f:
                                #    self.known_face_encodings = []
                                #    self.known_face_encodings = pickle.load(f)
                                self.known_face_encodings.append(encoding)
                                #with open(pickle_file_path, "wb") as f:
                                #    pickle.dump(self.known_face_encodings, f)
                                
                            except Exception as e:
                                print(e)
                    
            self.framecounter += 1
            
            self.process_current_frame = not self.process_current_frame

            for (top, right, bottom, left), name in zip(self.face_locations, self.face_names):
                # Resizes image 4x
                top *= 4
                bottom *= 4
                right *= 4
                left *= 4

                # Sets the basic square color red
                square_color = (0, 0, 255)

                # Strips the confidence from the name and appends it to name_list
                self.name_list.append(name)

                # If list is larger than 20 it prints and clears it to allow mult. faces
                if len(self.name_list) > 20:
                    print(self.name_list)
                    self.name_list = []

                # If list is larger that 2 it takes the mode of the list, and if exception, 
                # takes random element from mult. mode
                elif len(self.name_list) > 2:
                    try:
                        name = statistics.mode(self.name_list)
                    except:
                        mult_names = statistics.multimode(self.name_list)
                        name = choice(mult_names)

                print(name)

                # Displays the frame and puts in the rectangle and text
                cv2.rectangle(frame, (left, top), (right, bottom), square_color, 2)
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), square_color, -1)
                cv2.putText(frame, f"{name}", (left + 6, bottom - 6),
                            cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1)

            cv2.imshow("Face recognition", frame)

            # Shutdown function
            if cv2.waitKey(1) == ord("q"):
                break
        
        video_capture.release()
        cv2.destroyAllWindows()

#Calculate face confidence percentage
def face_confidence(face_distace, face_match_threshold=0.6):
    range = (1.0 - face_match_threshold)
    linear_val = (1.0 - face_distace) / (range * 2.0)

    if face_distace > face_match_threshold:
        return str(round(linear_val * 100, 2)) + "%"
    else:
        value = (linear_val + ((1.0 - linear_val) * math.pow((linear_val - 0.5) * 2, 0.2))) * 100
        return str(round(value, 2)) + "%"

# Creates a donwload folder in the main directory with tha name "subfolder"
def create_download_folder(subfolder):
    main_directory = os.path.dirname(os.path.realpath(__file__))
    download_folder = os.path.join(main_directory, subfolder)

    if not os.path.exists(download_folder):
        try:
            os.makedirs(download_folder)
            print(f"Download folder created: {download_folder}")
        except Exception as e:
            print(f"Error creating download folder: {e}")


# Strips the data in parenthesis from a string
def strip_string(input_string):
    string = re.sub(r'\([^)]*\)$', '', input_string)
    return string


#Creates donwload folder and runs the run_recognition function of the FaceRecognition class
if __name__ == "__main__":
    create_download_folder("faces")
    fr = FaceRecognition()
    fr.run_recognition()