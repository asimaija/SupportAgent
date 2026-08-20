from pathlib import Path

# Relative path (was previously hardcoded to a Windows "D:\..." path,
# which breaks the moment this project runs on any other machine,
# OS, or deployment environment).
BASE_DIR = Path(__file__).resolve().parent.parent
dataset_path = BASE_DIR / "dataset" / "appinsnap.txt"


def load_dataset():
    with open(dataset_path, "r", encoding="utf-8") as file:
        return file.read()


text = load_dataset()

print("Dataset Loaded Successfully!")
print("Characters:", len(text))
print("Words:", len(text.split()))

print("\nPreview:")
print(text[:1000])