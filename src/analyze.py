import pandas as pd
import glob

def load_data(folder="data"):
    files = glob.glob(f"{folder}/*.csv")
    df = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)
    return df

if __name__ == "__main__":
    df = load_data()
    print("Toplam satır:", df.shape[0])
    print()
    print("Kullanıcı adı başına bulunan hesap sayısı:")
    print(df[df["exists"] == "Claimed"].groupby("username").size())