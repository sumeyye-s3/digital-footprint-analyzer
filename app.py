import sys
import glob
import pandas as pd
import plotly.express as px
import streamlit as st

sys.path.append("src")
from risk_analysis import PLATFORM_TO_CAT, WEIGHTS, risk_level

st.set_page_config(page_title="Digital Footprint Risk Analyzer", layout="wide")
st.title("🔍 Digital Footprint Risk Analyzer")
st.caption("Kullanıcı adı yeniden kullanımının sosyal mühendislik risk analizi. "
           "Bu demodaki veriler sentetiktir.")

# --- Veri kaynağı ---
uploaded = st.sidebar.file_uploader(
    "Sherlock CSV dosyalarını yükle", type="csv", accept_multiple_files=True)

if uploaded:
    df = pd.concat([pd.read_csv(f) for f in uploaded], ignore_index=True)
    st.sidebar.success(f"{len(uploaded)} dosya yüklendi")
else:
    files = glob.glob("data/*.csv")
    df = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)
    st.sidebar.info("Örnek (sentetik) veri gösteriliyor")

df["category"] = df["name"].map(PLATFORM_TO_CAT).fillna("Diğer")
df["weight"] = df["category"].map(WEIGHTS).fillna(1)

found = df[df["exists"] == "Claimed"]
total_weight = df[df["username"] == df["username"].iloc[0]]["weight"].sum()

scores = pd.DataFrame({
    "Hesap sayısı": found.groupby("username").size(),
    "Risk skoru": (found.groupby("username")["weight"].sum() / total_weight * 100).round(1),
}).sort_values("Risk skoru", ascending=False)
scores["Seviye"] = scores["Risk skoru"].apply(risk_level)

# --- Üst metrikler ---
cols = st.columns(len(scores))
for col, (user, row) in zip(cols, scores.iterrows()):
    col.metric(user, f"{row['Risk skoru']}/100", f"{row['Seviye']} · {row['Hesap sayısı']} hesap",
               delta_color="off")

# --- Grafikler ---
left, right = st.columns(2)

with left:
    fig = px.bar(scores.reset_index(), x="username", y="Risk skoru",
                 color="Risk skoru", color_continuous_scale="Reds",
                 title="Risk Skoru")
    st.plotly_chart(fig, use_container_width=True)

with right:
    cat = found.groupby(["category", "username"]).size().reset_index(name="Hesap")
    fig = px.bar(cat, x="category", y="Hesap", color="username",
                 barmode="group", title="Kategori Dağılımı")
    st.plotly_chart(fig, use_container_width=True)

pivot = found.pivot_table(index="username", columns="category",
                          values="name", aggfunc="count", fill_value=0)
fig = px.imshow(pivot, text_auto=True, color_continuous_scale="Reds",
                title="Kullanıcı Adı x Kategori Isı Haritası")
st.plotly_chart(fig, use_container_width=True)

# --- Detay ve öneri ---
st.subheader("Detay")
selected = st.selectbox("Kullanıcı adı seç", scores.index)
st.dataframe(found[found["username"] == selected][["name", "category", "url_user"]],
             use_container_width=True)

row = scores.loc[selected]
st.subheader("Öneriler")
if row["Seviye"] == "DÜŞÜK":
    st.success("Maruz kalma düşük. Mevcut alışkanlıkları sürdür.")
else:
    st.warning(f"{row['Hesap sayısı']} platformda aynı kullanıcı adı kullanılıyor. "
               "Platformlara farklı kullanıcı adı seç, profil bilgilerini azalt, "
               "e-posta takma adları kullan.")

# --- Rapor indirme ---
st.download_button("Skor raporunu indir (CSV)", scores.to_csv().encode("utf-8"),
                   "risk_report.csv", "text/csv")