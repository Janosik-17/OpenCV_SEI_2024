import cv2
import numpy as np
import face_recognition
import os
import sys
import math
from requests_html import HTMLSession
from bs4 import BeautifulSoup

session = HTMLSession()

# Calculate face confidence percentage
def face_confidence(face_distance, face_match_threshold=0.6):
    face_range = (1.0 - face_match_threshold)
    linear_val = (1.0 - face_distance) / (face_range * 2.0)

    if face_distance > face_match_threshold:
        return str(round(linear_val * 100, 2)) + "%"
    else:
        value = (linear_val + ((1.0 - linear_val) * math.pow((linear_val - 0.5) * 2, 0.2))) * 100
        return str(round(value, 2)) + "%"


class ImageScraper:
    def __init__(self, base_url, koncovky):
        self.base_url = base_url
        self.koncovky = koncovky
        self.img_list = []

    def scrape_site(self, url_input):
        img_list = []
        info_list = []
        url = self.base_url + url_input
        page = session.get(url).content
        soup = BeautifulSoup(page, "html.parser")
        content = soup.find("div", class_="entry-content")
        content_divs = content.find_all("div", class_="wp-block-image")
        content_divs2 = content.find_all("figure", class_="wp-block-image size-large")
        content_info = content.find_all("h3", class_="wp-block-heading has-text-align-left")
        for div in content_divs:
            under_div = div.find("img")
            img_src = under_div.get("src")
            img_list.append(img_src.encode("utf-8"))
        for fig in content_divs2:
            under_fig = fig.find("img")
            img_src = under_fig.get("src")
            img_list.append(img_src.encode("utf-8"))
        for inf in content_info:
            under_inf = inf.find("strong")
            info = under_inf.get_text().encode("utf-8")
            info_list.append(info)
        return img_list, info_list

    def compile_list(self, input_list):
        output_list = []
        for element in input_list:
            for element_2 in element:
                output_list.append(element_2)
        return output_list

    def scrape_all(self):
        over_img_list = []
        over_info_list = []
        for num in range(len(self.koncovky)):
            ret_img_list, ret_info_list = self.scrape_site(self.koncovky[num])
            over_img_list.append(ret_img_list)
            over_info_list.append(ret_info_list)
        self.img_list = self.compile_list(over_img_list)
        return over_img_list, over_info_list


class FaceRecognition:
    face_locations = []
    face_encodings = []
    face_names = []
    known_face_names = []
    known_face_encodings = []
    process_current_frame = True

    def __init__(self, scraper):
        self.scraper = scraper
        self.encode_faces()

    def encode_faces(self):
        for img_data in self.scraper.img_list:
            try:
                img_url = session.get(img_data)  # Decode bytes to string
                response = session.get(img_url)
                face_image = face_recognition.load_image_file(response.content)
                face_encoding = face_recognition.face_encodings(face_image)[0]
                self.known_face_encodings.append(face_encoding)
                self.known_face_names.append(os.path.basename(img_url))
            except (IndexError, Exception) as e:
                print(f"Error encoding face: {e}")

    def run_recognition(self):
        video_capture = cv2.VideoCapture(0)

        if not video_capture.isOpened():
            sys.exit("Video source not found...")

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

                    face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
                    best_match_index = np.argmin(face_distances)

                    if matches[best_match_index]:
                        name = self.known_face_names[best_match_index]
                        confidence = face_confidence(face_distances[best_match_index])

                    self.face_names.append(f"{name} ({confidence})")

            self.process_current_frame = not self.process_current_frame

            # Display annotations
            for (top, right, bottom, left), name in zip(self.face_locations, self.face_names):
                top *= 4
                bottom *= 4
                right *= 4
                left *= 4

                cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), -1)
                cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1)

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


if __name__ == "__main__":
    base_url = "https://bilgym.sk/"
    koncovky = ["programy-a-projekty-skoly/", "nepedagogicka-podpora/", "kontakt-podporny-tim/",
                "kontakt-ucitelia/", "spravna-rada/", "kontakt-vedenie-skoly/"]
    
    faces_folder = "/faces"
    create_download_folder(faces_folder)

    # Create the ImageScraper instance
    scraper = ImageScraper(base_url, koncovky)

    # Download and save images using scraper
    scraper.scrape_all()

    # Create the download folder if it doesn't exist
    

    # Initialize and run face recognition using ImageScraper
    fr = FaceRecognition(scraper)
    fr.run_recognition()
