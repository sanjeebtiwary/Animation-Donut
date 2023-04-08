import PySimpleGUI as sg
import subprocess
import os


# Define the layout of the GUI
layout = [
    [sg.Text("Welcome to the Donut Animation!")],
    [sg.Image(filename="", key="-IMAGE-")],
    [sg.Button("Start", key="-START-"), sg.Button("Stop", key="-STOP-"), sg.Button("Exit", key="-EXIT-")]
]

# Create the window with the defined layout
window = sg.Window("Donut Animation", layout)

# Start the C++ backend process
backend_process = subprocess.Popen(["D:\Project\Animation Donut\donut_animation.cpp"])

# Event loop for the GUI
while True:
    event, values = window.read(timeout=50)
    if event == sg.WINDOW_CLOSED or event == "-EXIT-":
        # Stop the C++ backend process and close the window
        backend_process.kill()
        break
    elif event == "-START-":
        # Restart the C++ backend process
        backend_process.kill()
        backend_process = subprocess.Popen(["./donut_animation"])
    elif event == "-STOP-":
        # Stop the C++ backend process
        backend_process.kill()
    # Update the image in the GUI window
    image_file = os.path.join(os.getcwd(), "donut_animation_output.txt")
    window["-IMAGE-"].update(filename=image_file)
    backend_process = subprocess.Popen(["donut_animation.exe"])


# Close the window and exit the program
window.close()
