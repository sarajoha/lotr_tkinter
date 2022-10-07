"""
Interface to query a table of forests from the Lord Of The Rings
Using the data from gvSIG https://scholarworks.wm.edu/asoer/3/
"""
from tkinter import *
import tkinter as tk
from tkinter import messagebox
import psycopg2 as db
from dotenv import load_dotenv
import os

load_dotenv()

host = os.getenv("HOST")
dbname = os.getenv("DBNAME")
user = os.getenv("USER")
password = os.getenv("PASSWORD")
port = os.getenv("PORT")
table = os.getenv("TABLE")

palette = {
    "darkBrown": "#261E1D",
    "mediumBrown": "#423730",
    "lightBrown": "#BC6C25",
    "darkRed": "#4F1C0D",
    "darkGreen": "#283618",
    "green": "#606C38",
    "lightGrey": "#BEB8AF"
}

# Connet to Database
dbConnection = db.connect(host=host, dbname=dbname, user=user, password=password, port=port)
conn = dbConnection.cursor()

# create actions
def new():
	"""
	Creates new window
	"""
	window = Tk()
	window.geometry("700x300+20+20")
	window.resizable(0,0)
	window.configure(bg=palette["green"], cursor="hand1")
	window.title("Neeeww")
	tk.Button(window, text="Exit", command=window.destroy).pack(side=BOTTOM)


def queryTable():
    """
    Query the database
    """
    field_id = recordId.get()
    conn.execute(f"SELECT gid, name, inhabitant, geom FROM {table} WHERE gid = {field_id}")
    result=conn.fetchall()

    for record in result:
        rlabel=Label(resultsFrame, text="GID", bg=palette["lightBrown"]).grid(row=11, column=1, sticky=E)
        rlabel=Label(resultsFrame, text="Nombre").grid(row=11, column=2, sticky=W) #sticky N E S W default center
        rlabel=Label(resultsFrame, text="Habitantes").grid(row=11, column=3)
        rlabel=Label(resultsFrame, text="Geom").grid(row=11, column=4)
        rlabel=Label(resultsFrame, text=record[0]).grid(row=12, column=1, sticky="W")
        rlabel=Label(resultsFrame, text=record[1]).grid(row=12, column=2, sticky="W")
        rlabel=Label(resultsFrame, text=record[2]).grid(row=12, column=3, sticky="W")
        rlabel=Label(resultsFrame, text=record[3][:20]).grid(row=12, column=4, sticky="W")
    dbConnection.commit()


def create_area_table():
    """
    Creates a table with the area of the selected element
    """
    field_id = recordId.get()
    if not field_id:
       return tk.messagebox.showinfo("Actualización", "Primero ingreso el dato a consultar") 
    conn.execute(f"CREATE TABLE {table}_area as SELECT gid, st_area(geom), geom FROM {table} WHERE gid = {field_id}")
    tk.messagebox.showinfo("Actualización", "Creación Exitosa!!")
    dbConnection.commit()


def clean():
    inputId.set("")
    recordId.delete(0, "end")


def close():
    """
    Closes the window, and asks for confirmation first
    """
    response = tk.messagebox.askquestion("Seguro?", "Quieres cerrar la ventana?")
    if response == "yes":
        window.destroy()
        return
    tk.messagebox.showinfo("Ok", "La ventana no se cerrará :)")


#######
# create main window
window = Tk()

# image = "Game-of-Thrones-logo.png"
# image = "icons/game-of-thrones-small.png"
image = "icons/lotr-small.png"
window.geometry("700x700+20+20")
window.resizable(1,1)
window.configure(bg=palette["darkGreen"], cursor="hand2")
window.title("Lord Of The Rings")
img = PhotoImage(file=image)
window.iconphoto(False, img)

# menu
menuBar = Menu(window)

# menu options
# File menu
menuFile = Menu(menuBar, tearoff=0)
menuFile.add_command(label="New", command=new)
menuFile.add_separator()
menuFile.add_command(label="Exit", command=window.quit)

# Edit menu
menuEdit = Menu(menuBar, tearoff=0)
menuEdit.add_command(label="Copy")
menuEdit.add_separator()
menuEdit.add_command(label="Paste")

# Add menus to menu bar and to window
menuBar.add_cascade(label="File", menu=menuFile)
menuBar.add_cascade(label="Edit", menu=menuEdit)
window.config(menu=menuBar)

# Add Frames
# add frame to input an id
inputFrame = Frame(window, width=400, height=100, bg=palette["green"])
inputFrame.pack(pady=10)

inputId = StringVar()
recordId = Entry(inputFrame, textvariable=id)
recordId.pack(pady=10, padx=10)

idLabel = Label(inputFrame, text="Ingrese el dato a consultar", bg=palette["green"], fg="white")
idLabel.pack(pady=5, padx=10)

# add frame to query the db with the id
actionFrame = Frame(window, width=400, height=100, bg=palette["green"])
actionFrame.pack(pady=20)

# add action buttons
bt = Button(actionFrame, text="Consultar", command=queryTable)
bt.grid(pady=5, padx=5, row=5, column=0)

bt = Button(actionFrame, text="Limpiar", command=clean)
bt.grid(pady=5, padx=5, row=5, column=1)

bt = Button(actionFrame, text="Cerrar", command=close)
bt.grid(pady=5, padx=5, row=5, column=2)

bt = Button(actionFrame, text="Area", command=create_area_table)
bt.grid(pady=5, padx=5, row=5, column=3)

# add results frame
resultsFrame = Frame(window, width=400, height=100, bg=palette["lightBrown"])
resultsFrame.pack(pady=30)


# Shows window
window.mainloop()
