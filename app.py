import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import os

# -----------------------------
# 1. VERİYİ YÜKLE
# -----------------------------
# Cloud üzerinde dosya yolunu garantiye alıyoruz
current_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(current_dir, "il_yil_ozet.csv")

@st.cache_data # Veriyi her seferinde baştan yüklemesin diye hızlandırıyoruz
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
# 3. SADECE 2023 VERİSİ
# -----------------------------
# Yıl kolonu sayısal değilse hata vermemesi için dönüştürüyoruz
df["yil"] = pd.to_numeric(df["yil"], errors='coerce')
df = df[df["yil"] == 2023]

# -----------------------------
# 4. EKSİK VERİ TEMİZLE
# -----------------------------
df = df.dropna(subset=["hastane_sayisi", "yatak_sayisi", "nufus"])

# -----------------------------
# 5. ORANLARI OLUŞTUR
# -----------------------------
df["hastane_oran"] = df["hastane_sayisi"] / df["nufus"]
df["yatak_oran"] = df["yatak_sayisi"] / df["nufus"]

# -----------------------------
# 6. STREAMLIT BAŞLIK
# -----------------------------
st.set_page_config(page_title="Türkiye Sağlık Analizi", page_icon="🏥")
st.title("🏥 Türkiye Sağlık Erişim Analizi")

# -----------------------------
# 7. İL SEÇ
# -----------------------------
il_listesi = sorted(df["il"].unique())
il_sec = st.selectbox("İl seçiniz", il_listesi)

# Seçilen ile göre filtrele
row = df[df["il"] == il_sec]

# -----------------------------
# 8. SEÇİLEN İL BİLGİSİ
# -----------------------------
if not row.empty:
    st.subheader(f"{il_sec} Verileri")
    
    # Hataları önlemek için .iloc[0] kullanarak tekil değerleri çekiyoruz
    h_oran = float(row["hastane_oran"].iloc[0])
    y_oran = float(row["yatak_oran"].iloc[0])
    
    col_a, col_b = st.columns(2)
    col_a.metric("Hastane Oranı (Kişi Başı)", f"{h_oran:.5f}")
    col_b.metric("Yatak Oranı (Kişi Başı)", f"{y_oran:.5f}")
else:
    st.error("Seçilen ile ait veri bulunamadı.")

# -----------------------------
# 9. EN İYİ / EN KÖTÜ İLLER
# -----------------------------
st.divider()
st.subheader("📊 En İyi ve En Kötü İller (Hastane Oranı)")

best = df.sort_values("hastane_oran", ascending=False).head(10)
worst = df.sort_values("hastane_oran", ascending=True).head(10)

col1, col2 = st.columns(2)

with col1:
    st.write("🏆 **En İyi 10 İl**")
    st.dataframe(best[["il", "hastane_oran"]], hide_index=True)

with col2:
    st.write("⚠️ **En Kötü 10 İl**")
    st.dataframe(worst[["il", "hastane_oran"]], hide_index=True)

# -----------------------------
# 10. GRAFİK - HASTANE ORANI
# -----------------------------
st.subheader("📈 Hastane Oranı Grafiği")

fig1, ax1 = plt.subplots(figsize=(10,5))
top10 = df.sort_values("hastane_oran", ascending=False).head(10)

ax1.barh(top10["il"], top10["hastane_oran"], color='skyblue')
ax1.set_xlabel("Hastane Oranı")
ax1.set_ylabel("İl")
ax1.set_title("En İyi 10 İl (Hastane Oranı)")
ax1.invert_yaxis()

st.pyplot(fig1)

# -----------------------------
# 11. GRAFİK - YATAK ORANI
# -----------------------------
st.subheader("📈 Yatak Oranı Grafiği")

fig2, ax2 = plt.subplots(figsize=(10,5))
top10_yatak = df.sort_values("yatak_oran", ascending=False).head(10)

ax2.barh(top10_yatak["il"], top10_yatak["yatak_oran"], color='salmon')
ax2.set_xlabel("Yatak Oranı")
ax2.set_ylabel("İl")
ax2.set_title("En İyi 10 İl (Yatak Oranı)")
ax2.invert_yaxis()

st.pyplot(fig2)
