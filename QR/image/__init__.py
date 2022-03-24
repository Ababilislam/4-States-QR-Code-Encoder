from typing import Iterator
from pathlib import Path
from PIL import Image, ImageOps

def list_images(path: Path) -> Iterator[Path]:
    return path.glob("**/*.jpg")

# assuming all the images are in ./data
img_paths = list(list_images(Path("./data")))
target_id = 5019      # just pick one

collage = Image.new("RGB", (1600, 400))
for i in range(4):
    panel = ImageOps.fit(Image.open(img_paths[target_id + i]), (400,400))
    collage.paste(panel, (i*400, 0))
collage.save("fig/collage.jpg")