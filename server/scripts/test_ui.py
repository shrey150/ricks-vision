from tkinter import *
import tkinter
import tkinter.ttk as ttk

print(tkinter.Tcl().eval('info patchlevel'))

def run_diagnostics():
    root = Tk()
    root.geometry("400x300")
    root.title("Tkinter Diagnostics")
    Label(root, text="Tkinter is working!", font=("Arial", 16)).pack(pady=20)

    Button(root, text="Test Button", command=lambda: print("Button Clicked")).pack(pady=10)
    Scale(root, from_=0, to=10, orient=HORIZONTAL).pack(pady=10)
    ttk.Progressbar(root, length=200).pack(pady=10)

    root.mainloop()

run_diagnostics()
