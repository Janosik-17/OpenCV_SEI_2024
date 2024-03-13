from tkinter import *
import cv2
import os
import sys

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


key = 1
video_capture = cv2.VideoCapture(0)
ret, frame = video_capture.read()
face_image = frame

if key == 1:
    main_directory = os.path.dirname(os.path.realpath(__file__))
    download_folder = os.path.join(main_directory, "faces")
    inputted_name = popup_window()
    filename = f"{inputted_name}.jpg"
    filepath = os.path.join(download_folder, filename)
    try: 
        cv2.imwrite(filepath, face_image)
        print("Success")
    except Exception as e:
        print("Error saving file:", e)
