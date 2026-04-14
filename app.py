import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# -----------------------------
# 1. VERİYİ YÜKLE
# -----------------------------
df = pd.read_csv("il_yil_ozet.csv")

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
st.title("🏥 Türkiye Sağlık Erişim Analizi")

# -----------------------------
# 7. İL SEÇ
# -----------------------------
il_sec = st.selectbox("İl seçiniz", sorted(df["il"].unique()))

row = df[df["il"] == il_sec]

# -----------------------------
# 8. SEÇİLEN İL BİLGİSİ
# -----------------------------
st.subheader(f"{il_sec} Verileri")

# Verinin boş olup olmadığını kontrol ederek yazdır
hastane_orani = row["hastane_oran"].values[0] if not row.empty else 0
st.write(f"Hastane Oranı: {hastane_orani:.2f}")
st.write("Yatak Oranı:", float(row["yatak_oran"]))

# -----------------------------
# 9. EN İYİ / EN KÖTÜ İLLER
# -----------------------------
st.subheader("📊 En İyi ve En Kötü İller")

best = df.sort_values("hastane_oran", ascending=False).head(10)
worst = df.sort_values("hastane_oran", ascending=True).head(10)

col1, col2 = st.columns(2)

with col1:
    st.write("🏆 En İyi 10 İl")
    st.dataframe(best[["il", "hastane_oran"]])

with col2:
    st.write("⚠️ En Kötü 10 İl")
    st.dataframe(worst[["il", "hastane_oran"]])

# -----------------------------
# 10. GRAFİK - HASTANE ORANI
# -----------------------------
st.subheader("📈 Hastane Oranı Grafiği")

fig1, ax1 = plt.subplots(figsize=(10,5))
top10 = df.sort_values("hastane_oran", ascending=False).head(10)

ax1.barh(top10["il"], top10["hastane_oran"])
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

ax2.barh(top10_yatak["il"], top10_yatak["yatak_oran"])
ax2.set_xlabel("Yatak Oranı")
ax2.set_ylabel("İl")
ax2.set_title("En İyi 10 İl (Yatak Oranı)")
ax2.invert_yaxis()

st.pyplot(fig2)
