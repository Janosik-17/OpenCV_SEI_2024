from tkinter import *
def button_clicked():
    input_name = input_text.get()
    window.destroy()
    return input_name

window = Tk()
window.title("saving a new face")
window.geometry("200x200")

disp_text = Label(window, text="Success", font=("Arial Bold", 25))
disp_text.grid(column = 0, row = 0)

button = Button(window, text= "Save", font=("Arial Bold", 12), bg="dark green", fg="white", command = button_clicked)
button.grid(column=0, row=2)

input_text = Entry(window, width=10)
input_text.grid(column=0, row=1)

input_text.get()

window.mainloop()