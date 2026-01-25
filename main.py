from typing import Optional
import fastapi
from fastapi.staticfiles import StaticFiles
from pathlib import Path

app = fastapi.FastAPI()

static_path = Path("static")
static_path.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=static_path), name="static")
animals = {}


@app.post("/animals/")
def create_animal(name: str, species: str):
    animal_id = len(animals) + 1
    animals[animal_id] = {"name": name, "species": species}
    return {"id": animal_id, "name": name, "species": species}


@app.get("/animals/")
def list_animals():
    return animals


@app.get("/animals/{animal_id}")
def get_animal(animal_id: int):
    return animals.get(animal_id, {"error": "Animal not found"})


@app.put("/animals/{animal_id}")
def update_animal(animal_id: int, name: str | None, species: str | None):
    if not name and not species:
        return {"error": "No update parameters provided"}
    if animal_id in animals:
        if name:
            animals[animal_id]["name"] = name
        if species:
            animals[animal_id]["species"] = species
        return animals[animal_id]
    return {"error": "Animal not found"}


@app.get("/")
def main():
    print(animals)
