import glob
import pandas as pd
import matplotlib.pyplot as plt

# Platform -> (kategori)
CATEGORIES = {
    "Sosyal Medya": ["Twitter", "Instagram", "Facebook", "TikTok", "Pinterest",
                     "Snapchat", "LinkedIn", "Telegram", "Discord"],
    "Geliştirici": ["GitHub", "GitLab", "StackOverflow", "HackerRank", "Kaggle", "Replit"],
    "Forum/Blog": ["Reddit", "Medium", "Quora", "Tumblr", "Goodreads", "Letterboxd", "Wattpad"],
    "Medya/Tasarım": ["Flickr", "Vimeo", "YouTube", "Twitch", "SoundCloud", "Spotify",
                      "Dribbble", "Behance", "DeviantArt", "Slideshare", "Scribd"],
    "Oyun": ["Steam", "Roblox", "Chess"],
    "Alışveriş": ["eBay", "Etsy", "Patreon"],
    "Eğitim": ["Duolingo"],
}

# Sosyal mühendislik açısından kategori ağırlığı (metodoloji kararı, README'de açıkla)
WEIGHTS = {
    "Sosyal Medya": 3, "Alışveriş": 3, "Geliştirici": 2, "Forum/Blog": 2,
    "Oyun": 1, "Medya/Tasarım": 1, "Eğitim": 1,
}

PLATFORM_TO_CAT = {p: c for c, plist in CATEGORIES.items() for p in plist}


def load_data(folder="data"):
    files = glob.glob(f"{folder}/*.csv")
    df = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)
    df["category"] = df["name"].map(PLATFORM_TO_CAT).fillna("Diğer")
    df["weight"] = df["category"].map(WEIGHTS).fillna(1)
    return df


def risk_scores(df):
    """Skor = bulunan hesapların ağırlık toplamı / tüm platformların ağırlık toplamı * 100"""
    total_weight = df[df["username"] == df["username"].iloc[0]]["weight"].sum()
    found = df[df["exists"] == "Claimed"]
    score = found.groupby("username")["weight"].sum() / total_weight * 100
    out = pd.DataFrame({
        "hesap_sayisi": found.groupby("username").size(),
        "risk_skoru": score.round(1),
    })
    return out.sort_values("risk_skoru", ascending=False)


def risk_level(s):
    return "YÜKSEK" if s >= 60 else "ORTA" if s >= 30 else "DÜŞÜK"


if __name__ == "__main__":
    df = load_data()
    found = df[df["exists"] == "Claimed"]
    scores = risk_scores(df)
    scores["seviye"] = scores["risk_skoru"].apply(risk_level)

    print("=== RİSK SKORLARI ===")
    print(scores, "\n")

    # Kullanıcı x kategori tablosu
    pivot = found.pivot_table(index="username", columns="category",
                              values="name", aggfunc="count", fill_value=0)
    print("=== KATEGORİ DAĞILIMI ===")
    print(pivot, "\n")

    # Grafik 1: risk skoru
    ax = scores["risk_skoru"].plot(kind="bar", color="#c0392b", figsize=(7, 4))
    ax.set_title("Kullanıcı Adı Başına Risk Skoru (0-100)")
    ax.set_ylabel("Risk skoru")
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig("reports/risk_scores.png", dpi=150)
    plt.close()

    # Grafik 2: kategori dağılımı
    pivot.T.plot(kind="bar", figsize=(9, 5))
    plt.title("Kategoriye Göre Bulunan Hesaplar")
    plt.ylabel("Hesap sayısı")
    plt.xlabel("Kategori")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    plt.savefig("reports/category_distribution.png", dpi=150)
    plt.close()

    # Grafik 3: ısı haritası
    fig, ax = plt.subplots(figsize=(9, 3.5))
    im = ax.imshow(pivot.values, cmap="Reds")
    ax.set_xticks(range(len(pivot.columns)), pivot.columns, rotation=30, ha="right")
    ax.set_yticks(range(len(pivot.index)), pivot.index)
    for i in range(pivot.shape[0]):
        for j in range(pivot.shape[1]):
            ax.text(j, i, pivot.values[i, j], ha="center", va="center")
    ax.set_title("Kullanıcı Adı x Kategori Isı Haritası")
    fig.colorbar(im)
    plt.tight_layout()
    plt.savefig("reports/heatmap.png", dpi=150)
    plt.close()

    # Öneri
    print("=== ÖNERİLER ===")
    for user, row in scores.iterrows():
        print(f"- {user}: {row['hesap_sayisi']} platformda hesap, "
              f"risk {row['risk_skoru']} ({row['seviye']}).")
        if row["seviye"] != "DÜŞÜK":
            print("  Platformlara farklı kullanıcı adı kullan, "
                  "herkese açık profil bilgilerini azalt.")
    print("\nGrafikler reports/ klasörüne kaydedildi.")