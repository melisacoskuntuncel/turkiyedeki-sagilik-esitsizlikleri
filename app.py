import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import os

# -----------------------------
# 1. VERİYİ YÜKLE
# -----------------------------
current_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(current_dir, "il_yil_ozet.csv")

@st.cache_data
def load_data():
    data = pd.read_csv(file_path)
    return data

df = load_data()

# -----------------------------
# 2. KOLON İSİMLERİNİ DÜZELT
# -----------------------------
df = df.rename(columns={
    "Hastane Sayısı - Ölçüm bazında": "hastane_sayisi",
    "Hastane Yatak Sayısı - Ölçüm bazında": "yatak_sayisi",
    "İbbs-Düzey1, İbbs-Düzey2, İl Ve İlçe Nüfusları - Ölçüm bazında": "nufus"
})

# -----------------------------
# 3. VERİ ÖN İŞLEME
# -----------------------------
df["yil"] = pd.to_numeric(df["yil"], errors='coerce')
df = df[df["yil"] == 2023]
df = df.dropna(subset=["hastane_sayisi", "yatak_sayisi", "nufus"])

# -----------------------------
# 4. ORANLARI OLUŞTUR (100.000 Kişi Başına)
# -----------------------------
# Sayıları daha okunabilir yapmak için 100.000 ile çarpıyoruz
df["hastane_oran"] = (df["hastane_sayisi"] / df["nufus"]) * 100000
df["yatak_oran"] = (df["yatak_sayisi"] / df["nufus"]) * 100000

# -----------------------------
# 5. STREAMLIT BAŞLIK
# -----------------------------
st.set_page_config(page_title="Türkiye Sağlık Analizi", page_icon="🏥", layout="wide")
st.title("🏥 Türkiye Sağlık Erişim Analizi (2023)")
st.caption("Veriler 100.000 kişi başına düşen sayıları temsil etmektedir.")

# -----------------------------
# 6. İL SEÇİMİ
# -----------------------------
il_sec = st.selectbox("İncelemek istediğiniz ili seçiniz:", sorted(df["il"].unique()))
row = df[df["il"] == il_sec]

# -----------------------------
# 7. SEÇİLEN İL METRİKLERİ
# -----------------------------
if not row.empty:
    st.subheader(f"📍 {il_sec} İli Detaylı Verileri")
    h_oran = float(row["hastane_oran"].iloc[0])
    y_oran = float(row["yatak_oran"].iloc[0])
    
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("100.000 Kişiye Düşen Hastane", f"{h_oran:.2f}")
    col_b.metric("100.000 Kişiye Düşen Yatak", f"{y_oran:.1f}")
    col_c.metric("Toplam Nüfus", f"{int(row['nufus'].iloc[0]):,}".replace(",", "."))
else:
    st.error("Veri bulunamadı.")

st.divider()

# -----------------------------
# 8. TABLOLAR (EN İYİ / EN KÖTÜ)
# -----------------------------
st.subheader("📊 Bölgesel Kıyaslama (100.000 Kişi Başına Hastane)")
col1, col2 = st.columns(2)

best = df.sort_values("hastane_oran", ascending=False).head(10)
worst = df.sort_values("hastane_oran", ascending=True).head(10)

with col1:
    st.success("🏆 **Erişimi En Yüksek 10 İl**")
    st.dataframe(best[["il", "hastane_oran"]].rename(columns={"hastane_oran": "Hastane Sayısı"}), hide_index=True, use_container_width=True)

with col2:
    st.warning("⚠️ **Erişimi En Düşük 10 İl**")
    st.dataframe(worst[["il", "hastane_oran"]].rename(columns={"hastane_oran": "Hastane Sayısı"}), hide_index=True, use_container_width=True)

# -----------------------------
# 9. GRAFİKLER
# -----------------------------
st.divider()
tab1, tab2 = st.tabs(["🏥 Hastane Oranı Grafiği", "🛌 Yatak Oranı Grafiği"])

with tab1:
    fig1, ax1 = plt.subplots(figsize=(10, 6))
    top10_h = df.sort_values("hastane_oran", ascending=False).head(10)
    colors = plt.cm.Blues(pd.np.linspace(0.8, 0.4, 10))
    ax1.barh(top10_h["il"], top10_h["hastane_oran"], color="skyblue")
    ax1.set_title("100.000 Kişi Başına En Çok Hastane Düşen İller")
    ax1.invert_yaxis()
    st.pyplot(fig1)

with tab2:
    fig2, ax2 = plt.subplots(figsize=(10, 6))
    top10_y = df.sort_values("yatak_oran", ascending=False).head(10)
    ax2.barh(top10_y["il"], top10_y["yatak_oran"], color="salmon")
    ax2.set_title("100.000 Kişi Başına En Çok Yatak Düşen İller")
    ax2.invert_yaxis()
    st.pyplot(fig2)
