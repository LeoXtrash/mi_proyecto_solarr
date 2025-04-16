import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime

# ----------- PARTE 1: Simulación base ----------- #
np.random.seed(42)
dias = 31
fechas = pd.date_range(start="2024-07-01", periods=dias, freq="D")

# Radiación solar simulada (kWh/m²)
media_radiacion = 6.5
std_radiacion = 1.0
radiacion = np.random.normal(media_radiacion, std_radiacion, dias)
radiacion = np.clip(radiacion, 0, None)

# Consumo con fines de semana más altos
consumo = []
for fecha in fechas:
    base = 6.5 if fecha.weekday() >= 5 else 5.0
    valor = base + np.random.normal(0, 0.5)
    consumo.append(max(valor, 0))

# Crear DataFrame
area_panel = 1.6
eficiencia_neta = 0.153

df = pd.DataFrame({
    "Fecha": fechas,
    "Radiación (kWh/m²)": radiacion,
    "Consumo (kWh)": consumo
})
df["Generación por panel (kWh)"] = df["Radiación (kWh/m²)"] * area_panel * eficiencia_neta

# ----------- STREAMLIT UI ----------- #
st.set_page_config(page_title="Dimensionamiento Solar", layout="wide")
st.title("🔆 Dimensionamiento de Paneles Solares - Madrid, Julio")

# Sidebar
st.sidebar.header("⚙️ Parámetros")
n_paneles = st.sidebar.slider("Número de paneles", 1, 20, 8)
simular_nublados = st.sidebar.checkbox("Simular 3 días nublados")

# Simulación días nublados
df_sim = df.copy()
if simular_nublados:
    i = np.random.randint(0, dias - 2)
    df_sim.loc[i:i+2, "Radiación (kWh/m²)"] *= 0.3
    df_sim["Generación por panel (kWh)"] = df_sim["Radiación (kWh/m²)"].values * area_panel * eficiencia_neta

# Generación total

df_sim["Generación total (kWh)"] = df_sim["Generación por panel (kWh)"] * n_paneles
df_sim["Cubre consumo"] = df_sim["Generación total (kWh)"] >= df_sim["Consumo (kWh)"]

# ----------- Gráfico principal ----------- #
st.subheader("📊 Generación vs Consumo Diario")
st.line_chart(df_sim.set_index("Fecha")[['Consumo (kWh)', 'Generación total (kWh)']])

# ----------- Métricas ----------- #
dias_cubiertos = df_sim["Cubre consumo"].sum()
porcentaje_cubierto = dias_cubiertos / dias * 100
st.metric("✅ Días cubiertos", f"{dias_cubiertos}/31 ({porcentaje_cubierto:.1f}%)")

# ----------- Gráfico de cobertura ----------- #
resultados = []
for n in range(1, 21):
    total = df["Generación por panel (kWh)"] * n
    cubiertos = (total >= df["Consumo (kWh)"].values).sum()
    resultados.append({"Paneles": n, "% Días Cubiertos": cubiertos / dias * 100})

df_resultados = pd.DataFrame(resultados)
st.subheader("📈 Cobertura vs Número de Paneles")
st.line_chart(df_resultados.set_index("Paneles"))

# ----------- Análisis económico ----------- #
costo_panel = 300  # €
precio_kWh = 0.20  # €/kWh
dias_anio = 365
gen_diaria = df["Generación por panel (kWh)"].mean()
gen_anual = gen_diaria * dias_anio * n_paneles
ahorro_anual = gen_anual * precio_kWh
costo_total = n_paneles * costo_panel
punto_equilibrio = costo_total / ahorro_anual

st.subheader("💰 Análisis Económico")
st.markdown(f"**Costo total del sistema:** €{costo_total:,.2f}")
st.markdown(f"**Ahorro anual estimado:** €{ahorro_anual:,.2f}")
st.markdown(f"**Energía generada al año:** {gen_anual:,.1f} kWh")
st.markdown(f"**Punto de equilibrio:** {punto_equilibrio:.1f} años")

# ----------- Footer ----------- #
st.markdown("---")
st.markdown("App desarrollada para el proyecto de dimensionamiento solar • Simulaciones en Madrid • Julio")
