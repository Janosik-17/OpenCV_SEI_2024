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
import time

def delete_all(conf):
    if conf == "y":
        main_directory = os.path.dirname(os.path.realpath(__file__))
        download_folder = os.path.join(main_directory, "faces")
        file_locations = [os.path.join(main_directory, "facial_encodings.pkl"), os.path.join(main_directory, "name_list.pkl")]
        for filename in os.listdir(download_folder):
            file_path = os.path.join(download_folder, filename)
            os.remove(file_path)
            print(f"Deleted {filename}")
        for file_path in file_locations:
            try:
                os.remove(file_path)
            except Exception as e:
                print(e)
        print("Files deleted...")
        return 0
    elif conf == "n":
        print("Files retained...")
        return 0

delete_all(input("Delete files before proceeding? y/n ...\n"))

def popup_window():
    window = Tk()
    window.title("Saving a new face")
    window.geometry("400x400")

    disp_text = Label(window, text="Success", font=("Arial Bold", 40))
    disp_text.grid(column=0, row=0)

    input_text = Entry(window, width=20)
    input_text.grid(column=0, row=1)

    # Function to retrieve input and close window
    def handle_save():
        global user_input
        user_input = input_text.get()  # Get input text
        window.destroy()  # Close the window

    button = Button(window, text="Save", font=("Arial Bold", 20), bg="dark green", fg="white", command=handle_save)
    button.grid(column=0, row=3)

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
    return inputted_name, filepath


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
        try:
            with open("name_list.pkl", "rb") as f:
                self.known_face_names = pickle.load(f)
                f.close()
        except Exception as e:
            print(e)
            for image in os.listdir("faces"):
                try:
                    self.known_face_names.append(image)
                    with open("name_list.pkl", "wb") as f:
                        pickle.dump(self.known_face_names, f)
                        f.close()
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
                rgb_small_frame = small_frame[:, :, ::1]

                #Finds all faces in the frame and makes their encodings
                self.face_locations = face_recognition.face_locations(rgb_small_frame)
                self.face_encodings = face_recognition.face_encodings(rgb_small_frame)
                self.face_names = []

                #For each face encoding in the image it is compared with the encoded faces in memory
                for face_encoding in self.face_encodings:
                    matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
                    name = "Unknown"

                    try:
                        #Finds the figurative distance between the saved faces and the face in the frame (Basically comparing them)
                        face_distaces = face_recognition.face_distance(self.known_face_encodings, face_encoding)
                        #The index of the best matching face is chosen
                        best_match_index = np.argmin(face_distaces)
                    except Exception as e:
                        print(e)

                    #The index of the best matching face corresponds to its registered filename
                    try:
                        if matches[best_match_index]:
                            name = self.known_face_names[best_match_index]
                    except Exception as e:
                        print(e)

                    self.face_names.append(name)

                    if self.framecounter >= 29:
                        try:
                            gay = statistics.mode(self.name_list)
                        except Exception as e:
                            print(e)
                            #Prevents the variable from being undefined, if the webcam doesnt register any face for a long time
                            gay = "nothing"
                        #If the face isnt recognised it is saved with an inputted name
                        if gay == "Unknown":
                            try:
                                #Reset the name mode list and the framecounter, create a popup to input the name and save the current frame by that name
                                self.framecounter = 0
                                self.name_list = []
                                new_name, filepath_new = save_img(frame)
                                self.known_face_names.append(new_name)
                                #Exception handling if the Image isnt saved for some reason (It will break the program on further starts, the pkl file must be removed and the saved image lost. I havent found a way around this it only has this problem on my computer because of github)
                                try:
                                    self.face_image = face_recognition.load_image_file(filepath_new)
                                    encoding = face_recognition.face_encodings(self.face_image)[0]
                                    encodings = [encoding, encoding]
                                except Exception as e:
                                    print(e)
                                    encoding = face_recognition.face_encodings(frame)[0]
                                    encodings = [encoding, encoding]
                                #This part of the code saves and loads the arrays from .pkl files in order to have them all be in the same dimensional array type variable, without this the program doesnt work
                                #It loads all the currently saved encodings
                                with open("facial_encodings.pkl", "rb") as f:
                                    self.known_face_encodings = []
                                    temp_pkl_list = []
                                    #Appends them to a temporary list
                                    for element in pickle.load(f):
                                        temp_pkl_list.append(element)
                                    f.close()
                                #Saves the new encoding within a list of itelf (to obtain the same type of array as the original saves have)
                                with open("facial_encodings_temp.pkl", "wb") as f:
                                    pickle.dump(encodings, f)
                                    f.close()
                                #Loads the newly saved encodings and appends it to the end of the known_face_encodings list which is utilized by this program to compare faces
                                with open("facial_encodings_temp.pkl", "rb") as f:
                                    encodings = pickle.load(f)
                                    #First the list was wiped and now its repopulated with the newly loaded encodings from the original .pkl
                                    for element in temp_pkl_list:
                                        self.known_face_encodings.append(element)
                                    #The new encoding is appended
                                    self.known_face_encodings.append(encodings[0])
                                    f.close()
                                #The temporary file is removed
                                os.remove("facial_encodings_temp.pkl")
                                #Here it resaves the currently running image encodings to a .pkl file, this eliminates the need to delete the .pkl file and reencode the saved images again
                                with open("facial_encodings.pkl", "wb") as f:
                                    pickle.dump(self.known_face_encodings, f)
                                    f.close()
                                with open("name_list.pkl", "wb") as f:
                                    pickle.dump(self.known_face_names, f)
                                    f.close()

                            except Exception as e:
                                print(e)
            #Provides a way to track the passage of frames, it is wiped in the save new face part of the program above
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
                head, sep, tail = name.partition(".")
                name=head

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
