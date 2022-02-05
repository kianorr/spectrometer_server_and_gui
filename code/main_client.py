from GUI_client import SpecApp, SaveData
import tkinter as tk

root = tk.Tk()
myapp = SpecApp(root)
root.geometry("900x550")
root.title("Spectrometer GUI")
root.config(bg='#345')
myapp.mainloop()