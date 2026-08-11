import pandas as pd



dataset_path = r"D:\Projects\SupportAgent\dataset\appinsnap.csv"

def load_dataset():
    df = pd.read_csv(dataset_path)
    return df


if __name__ == "__main__":
    df = load_dataset()
    print("Dataset Loaded sucessfully!")
    print("Total Records :" , len(df))
    
    