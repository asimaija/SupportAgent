dataset_path = r"D:\Projects\SupportAgent\dataset\appinsnap.txt"

def load_dataset():
    with open(dataset_path, "r", encoding="utf-8") as file:
        return file.read()


text = load_dataset()

print("Dataset Loaded Successfully!")
print("Characters:", len(text))
print("Words:", len(text.split()))

print("\nPreview:")
print(text[:1000])