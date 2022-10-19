from dotenv import load_dotenv

load_dotenv()


def transform_to_geojson():
    import geopandas as gpd
    TABLES = [
        "Bays",
        "Fields",
        "Forests",
        "Hills",
        "Islands",
        "Mountains",
        "Swamps",
        "Valleys"
    ]

    path = os.getenv("SHP_PATH")

    for table in TABLES:
        file = f"{path}/{table}.shp"

        shp_file = gpd.read_file(file)
        shp_file = shp_file.to_crs(epsg=4326)

        shp_file.to_file(f"./project/data/{table}.geojson", driver='GeoJSON')


def resize_image():
    from PIL import Image
    import glob

    for infn in glob.glob("project/icons/*.png"):
        # only for images that are not small already
        if infn.endswith("small.png"):
            continue
        outfn = infn.replace(".png", "-small.png")
        im = Image.open(infn)
        im.thumbnail((100, 100))
        im.save(outfn)