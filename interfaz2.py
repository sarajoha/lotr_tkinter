"""
Interface to query a table of forests from the Lord Of The Rings
Using the data from gvSIG https://scholarworks.wm.edu/asoer/3/
Color palette: https://coolors.co/palette/606c38-283618-fefae0-dda15e-bc6c25
# webbroser y folium
"""
from tkinter import *
import tkinter as tk
from tkinter import messagebox
import psycopg2 as db
from dotenv import load_dotenv
import os
import folium
import webbrowser


load_dotenv()

# TODO: organize code and separate buttons

host = os.getenv("HOST")
dbname = os.getenv("DBNAME")
user = os.getenv("USER")
password = os.getenv("PASSWORD")
port = os.getenv("PORT")

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
	window.geometry("900x300+20+20")
	window.resizable(0,0)
	window.configure(bg=palette["green"], cursor="hand1")
	window.title("Neeeww")
	tk.Button(window, text="Exit", command=window.destroy).pack(side=BOTTOM)


def cleanFrame():
    for widget in resultsFrame.winfo_children():
        widget.destroy()

def queryTable():
    """
    Query the database
    """
    field_id = recordId.get()
    conn.execute(f"SELECT gid, name, inhabitant, geom FROM {table.get()} WHERE gid = {field_id}")
    result=conn.fetchall()

    cleanFrame()

    if not result:
        label=Label(resultsFrame, text="Intenta con un numero menor")
        label.pack()
    # si no hay resultados mensaje

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


def calculate_area():
    """
    Creates a table with the area of the selected element
    """
    field_id = recordId.get()
    if not field_id:
       return tk.messagebox.showinfo("Actualización", "Primero ingreso el dato a consultar") 
    conn.execute(f"SELECT name, st_area(geom) FROM {table.get()} WHERE gid = {field_id}")
    result=conn.fetchall()[0]
    dbConnection.commit()

    name, area = result

    cleanFrame()

    label=Label(resultsFrame, text=f"El area de {name} es: {area:0.2f} km2")
    label.pack()


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


def count():
    conn.execute(f"SELECT COUNT(*) FROM {table.get()}")
    result=conn.fetchall()[0][0]
    dbConnection.commit()

    cleanFrame()

    label=Label(resultsFrame, text=f"Hay {result}")
    label.pack()


def largest_area():
    conn.execute(f"SELECT name, st_area(geom) FROM {table.get()} ORDER BY 2 DESC LIMIT 1")
    result=conn.fetchall()[0]
    dbConnection.commit()

    name, area = result

    cleanFrame()

    label=Label(resultsFrame, text=f"El lugar mas grande es: {name} y su area es: {area:0.2f} km2")
    label.pack()


def was_frodo_here():
    # intersect ?
    field_id = recordId.get()
    if not field_id:
       return tk.messagebox.showinfo("Actualización", "Primero ingreso el dato a consultar") 
    query = """SELECT st_intersects(polygonA, frodo_line) as contains_frodo
                from (select 
                        (select geom from {0} where gid = {1}) as polygonA,
                        (select geom from frodo_route where gid = 1) as frodo_line) as foo;"""
    conn.execute(query.format(table.get(), field_id))
    result=conn.fetchall()[0][0]
    dbConnection.commit()

    cleanFrame()

    if result:
        rtext = "Frodo estuvo aquí"
    else:
        rtext = "No :("

    label=Label(resultsFrame, text=rtext)
    label.pack()


def map_record():
    # centroide
    field_id = recordId.get()
    if not field_id:
       return tk.messagebox.showinfo("Actualización", "Primero ingreso el dato a consultar") 
    conn.execute(f"SELECT st_astext(st_transform(st_centroid(geom), 4326)) FROM {table.get()} WHERE gid = {field_id}")
    result=conn.fetchall()[0][0]
    dbConnection.commit()

    xy = result.split(' ')
    long = xy[0].split("POINT(")[1]
    lat = xy[1].split(")")[0]

    # transform to GEO Json and upload to github
    url = os.getenv("DATA_URL")
    layer = f"{url}/{table.get().title()}.geojson"

    centroid = [lat, long]
    m = folium.Map(
        location=centroid,
        tiles="cartodbpositron",
        zoom_start=8,
    )

    folium.GeoJson(layer, name="geojson").add_to(m)

    folium.LayerControl().add_to(m)
    map_path = f"./maps/{table.get()}_map.html"
    m.save(map_path)
    root_path = os.getenv("ROOT_PATH")
    full_path = os.path.join(root_path, map_path[2:])
    webbrowser.open_new_tab(full_path)


#######
# create main window
window = Tk()

# image = "Game-of-Thrones-logo.png"
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
# add frame to choose a table
gandalf = "icons/gandalf-small.png"
gandalf = PhotoImage(file=gandalf)

tableFrame = Frame(window, width=400, height=100, bg=palette["green"])
tableFrame.pack(padx=10, pady=10, side=TOP)
# tableFrame.pack(padx=10, pady=10, side=TOP, anchor=NW)

label = Label(tableFrame, image=gandalf, bg=palette["green"])
label.pack()

OPTIONS = [
    "bays",
    "fields",
    "forests",
    "hills",
    "islands",
    "mountains",
    "swamps",
    "valleys"
]
table = StringVar()
table.set(OPTIONS[0]) # default value

w = OptionMenu(tableFrame, table, *OPTIONS)
w.pack(pady=5, padx=10)


idLabel = Label(tableFrame, text="¡Bienvenido humano! ¿Que secretos de la Tierra Media deseas explorar?", bg=palette["green"], fg="white")
idLabel.pack(pady=10, padx=10)

# add frame to input an id
inputFrame = Frame(window, width=400, height=100, bg=palette["green"])
inputFrame.pack(side=TOP)
# inputFrame.pack(padx=10, pady=10, side=TOP)

inputId = StringVar()
recordId = Entry(inputFrame, textvariable=id)
recordId.pack(pady=10, padx=10)

# change when table changes?
idLabel = Label(inputFrame, text=f"Ingresa un número... si te atreves", bg=palette["green"], fg="white")
idLabel.pack(pady=5, padx=10) 

# add frame to query the db with the id
actionFrame = Frame(window, width=400, height=100, bg=palette["green"])
actionFrame.pack(pady=20)

# add results frame
resultsFrame = Frame(window, width=400, height=100, bg=palette["lightBrown"])
resultsFrame.pack(pady=30)

# add action buttons
bt = Button(actionFrame, text="Consultar", command=queryTable)
bt.grid(pady=5, padx=5, row=5, column=0)

bt = Button(actionFrame, text="Limpiar", command=clean)
bt.grid(pady=5, padx=5, row=5, column=1)

bt = Button(actionFrame, text="Cerrar", command=close)
bt.grid(pady=5, padx=5, row=5, column=2)

# how many are there
bt = Button(actionFrame, text="Cuantos hay?", command=count)
bt.grid(pady=5, padx=5, row=5, column=3)

# how big is x?
bt = Button(actionFrame, text="Area", command=calculate_area)
bt.grid(pady=5, padx=5, row=5, column=4)

# what x is the biggest?
bt = Button(actionFrame, text="Region mas grande?", command=largest_area)
bt.grid(pady=5, padx=5, row=5, column=5)

# # was frodo here?
bt = Button(actionFrame, text="Was Frodo here?", command=was_frodo_here)
bt.grid(pady=5, padx=5, row=5, column=6)

# # see in a map
bt = Button(actionFrame, text="See in a map", command=map_record)
bt.grid(pady=5, padx=5, row=5, column=7)



# Shows window
window.mainloop()
