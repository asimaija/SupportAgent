dataset_path = r"D:\Projects\SupportAgent\dataset\appinsnap.txt"


def load_dataset():

    with open(
        dataset_path,
        "r",
        encoding="utf-8"
    ) as file:

        text = file.read()

    return text


if __name__ == "__main__":

    text = load_dataset()

    print(
        "Dataset Loaded Successfully!"
    )

    print(
        "Total Characters:",
        len(text)
    )

    print(
        "Total Words:",
        len(text.split())
    )

    print("\nDataset Preview:")
    print(text[:9000])