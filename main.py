import cv2
import numpy as np
import face_recognition
import os, sys
import math
import pickle
import re

#Calculate face confidence percentage
def face_confidence(face_distace, face_match_threshold=0.6):
    range = (1.0 - face_match_threshold)
    linear_val = (1.0 - face_distace) / (range * 2.0)

    if face_distace > face_match_threshold:
        return str(round(linear_val * 100, 2)) + "%"
    else:
        value = (linear_val + ((1.0 - linear_val) * math.pow((linear_val - 0.5) * 2, 0.2))) * 100
        return str(round(value, 2)) + "%"


class FaceRecognition:
    face_locations = []
    face_encodings = []
    face_names = []
    known_face_names = []
    known_face_encodings = []
    process_current_frame = True
    name_list = []


    def __init__(self):
        self.encode_faces()
    

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


    def run_recognition(self):
        video_capture = cv2.VideoCapture(0)

        if not video_capture.isOpened():
            sys.exit("Video source not found...")

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
                    confidence = "Unknown"

                    face_distaces = face_recognition.face_distance(self.known_face_encodings, face_encoding)
                    best_match_index = np.argmin(face_distaces)

                    if matches[best_match_index]:
                        name = self.known_face_names[best_match_index]
                        confidence = face_confidence(face_distaces[best_match_index])
                    self.face_names.append(f"{name} ({confidence})")

            self.process_current_frame = not self.process_current_frame

            for (top, right, bottom, left), name in zip(self.face_locations, self.face_names):
                top *= 4
                bottom *= 4
                right *= 4
                left *= 4

                if confidence != "Unknown":
                    square_color = (0, 255, 0)  # Green for known faces
                else:
                    square_color = (0, 0, 255)  # Red for unknown faces

                # name = strip_string(name)

                cv2.rectangle(frame, (left, top), (right, bottom), square_color, 2)
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), square_color, -1)
                cv2.putText(frame, name, (left + 6, bottom - 6),
                            cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1)
                if len(self.name_list) > 0:
                    if self.name_list[0] == name:
                        self.name_list.append(name)
                    elif len(self.name_list) >= 10:
                        name = self.name_list[0]
                    elif len(self.name_list) >= 150:
                        self.name_list.clear()
                    else:
                        self.name_list.clear()
                    print(name)

            cv2.imshow("Face recognition", frame)

            if cv2.waitKey(1) == ord("q"):
                break
        
        video_capture.release()
        cv2.destroyAllWindows()


def create_download_folder(subfolder):
    main_directory = os.path.dirname(os.path.realpath(__file__))
    download_folder = os.path.join(main_directory, subfolder)

    if not os.path.exists(download_folder):
        try:
            os.makedirs(download_folder)
            print(f"Download folder created: {download_folder}")
        except Exception as e:
            print(f"Error creating download folder: {e}")


def strip_string(input_string):
    string = re.sub(r'\([^)]*\)$', '', input_string)
    return string

if __name__ == "__main__":
    create_download_folder("faces")
    fr = FaceRecognition()
    fr.run_recognition()