import os
import joblib
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="AgroData Caldas IA",
    page_icon="☕",
    layout="wide",
)


@st.cache_resource
def cargar_artefactos():
    ruta_modelo = "modelo_agrodata_caldas.joblib"
    ruta_escalador = "escalador_agrodata_caldas.joblib"
    ruta_meta = "metadata_modelo.joblib"

    if not (os.path.exists(ruta_modelo) and os.path.exists(ruta_escalador)):
        st.error("Faltan los archivos .joblib del modelo en el repositorio.")
        st.stop()

    modelo = joblib.load(ruta_modelo)
    escalador = joblib.load(ruta_escalador)
    metadata = joblib.load(ruta_meta) if os.path.exists(ruta_meta) else {}
    return modelo, escalador, metadata


modelo, escalador, metadata = cargar_artefactos()

st.title("☕ AgroData Caldas IA")
st.subheader("Sistema de Evaluación de Riesgo y Control de Calidad en Acopio de Café")
st.markdown("---")

col_izq, col_der = st.columns(2)

with col_izq:
    st.markdown("### Parámetros del lote")
    humedad = st.number_input(
        "Humedad del grano (%)",
        min_value=10.0,
        max_value=25.0,
        value=12.5,
        step=0.1,
    )
    merma = st.number_input(
        "Merma estimada (%)",
        min_value=0.0,
        max_value=35.0,
        value=5.0,
        step=0.5,
    )
    peso = st.number_input(
        "Peso total del lote (kg)",
        min_value=1.0,
        max_value=5000.0,
        value=250.0,
        step=10.0,
    )
    precio = st.number_input(
        "Precio de referencia por carga (COP)",
        min_value=100000.0,
        max_value=5000000.0,
        value=1750000.0,
        step=50000.0,
    )
    dias = st.number_input(
        "Días de secado",
        min_value=1,
        max_value=20,
        value=5,
        step=1,
    )
    evaluar = st.button("Evaluar lote de café", use_container_width=True)

with col_der:
    st.markdown("### Resultado de la evaluación")
    if evaluar:
        columnas_exactas = [
            "humedad_pct",
            "merma_estimada_pct",
            "peso_kg",
            "precio_referencia_cop",
            "dias_secado",
        ]
        entrada = pd.DataFrame(
            [[humedad, merma, peso, precio, dias]],
            columns=columnas_exactas,
        )
        entrada_escalada = escalador.transform(entrada)
        prob_alerta = float(modelo.predict_proba(entrada_escalada)[0][1])
        umbral = float(metadata.get("umbral_preventivo_optimo", 0.20))

        st.metric("Probabilidad de alerta (Clase 1)", f"{prob_alerta * 100:.2f}%")
        st.caption(f"Umbral preventivo configurado: {umbral * 100:.0f}%")

        if prob_alerta >= umbral:
            st.error("Clase 1 — Alerta / Revisión prioritaria")
            st.write(
                "Acción recomendada: verificar humedad en laboratorio y validar el secado antes de almacenar."
            )
        else:
            st.success("Clase 0 — Operación regular")
            st.write(
                "Acción recomendada: el lote cumple los parámetros base y puede continuar al flujo normal."
            )
    else:
        st.info("Ingresa los datos del lote y presiona 'Evaluar lote de café'.")