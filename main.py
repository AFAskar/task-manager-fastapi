from typing import Annotated, Literal
import fastapi
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from pydantic import BaseModel

app = fastapi.FastAPI()

static_path = Path("static")
static_path.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=static_path), name="static")
animals = {}


class Animal(BaseModel):
    name: str
    species: Literal["feline", "canine", "avian", "reptile", "amphibian", "fish"]


@app.post("/animals/")
def create_animal(animal: Annotated[Animal, fastapi.Query()]):
    animal_id = len(animals) + 1
    animals[animal_id] = {"name": animal.name, "species": animal.species}
    return {"id": animal_id, "name": animal.name, "species": animal.species}


@app.get("/animals/")
def list_animals():
    return animals


@app.get("/animals/{animal_id}")
def get_animal(animal_id: int):
    return animals.get(animal_id, {"error": "Animal not found"})


@app.get("/animals/{species}")
def get_all_by_species(species: str):
    result = {aid: info for aid, info in animals.items() if info["species"] == species}
    return result


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
