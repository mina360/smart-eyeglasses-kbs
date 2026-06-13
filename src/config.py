from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

GLASSES_DATA_PATH = str(BASE_DIR / "data" / "glasses_cleaned_augmented_filled.xlsx")
IMAGE_PATH = str(BASE_DIR / "sample_images" / "image.png")
UPLOAD_DIR = BASE_DIR / "static" / "uploads"