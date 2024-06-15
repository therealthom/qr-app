import streamlit as st
import pandas as pd
import qrcode
import base64
from io import BytesIO
import zipfile


# Función para generar QR
def generate_qr(data):
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()


# Función para crear URL con parámetros GET
def create_url(base_url, params):
    return f"{base_url}?{'&'.join([f'{key}={value}' for key, value in params.items()])}"


# Función para crear un archivo ZIP en memoria
def create_zip(qr_images):
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for idx, img in enumerate(qr_images):
            zip_file.writestr(f'qr_code_{idx + 1}.png', img)
    zip_buffer.seek(0)
    return zip_buffer


# Función para mostrar QR en una tabla
def display_qr_table(qr_data):
    table = f"<table><tr><th>Parametros</th><th>URL</th><th>QR Code</th></tr>"
    for data in qr_data:
        params = ", ".join([f"{key}: {value}" for key, value in data[0].items()])
        qr_code_base64 = base64.b64encode(data[2]).decode("utf-8")
        qr_code_img = f'<img src="data:image/png;base64,{qr_code_base64}" width="100">'
        table += f"<tr><td>{params}</td><td>{data[1]}</td><td>{qr_code_img}</td></tr>"
    table += "</table>"
    st.markdown(table, unsafe_allow_html=True)


# Título de la aplicación
st.title("Generador de QRs")

# Carga del archivo
uploaded_file = st.file_uploader("Sube tu archivo XLSX", type=["xlsx"])

if uploaded_file:
    xls = pd.ExcelFile(uploaded_file)
    sheet_names = xls.sheet_names

    # Selección de hoja
    sheet_name = st.selectbox("Selecciona la hoja", sheet_names)

    if sheet_name:
        df = pd.read_excel(uploaded_file, sheet_name=sheet_name)
        st.write("Datos de la hoja seleccionada:", sheet_name)
        st.write(df)

        # Selección de columnas de inicio
        columns = df.columns.tolist()
        selected_columns = st.multiselect("Selecciona las columnas de inicio", columns)

        if selected_columns:
            start_row_index = st.selectbox("Selecciona el índice de la fila de inicio", df.index.tolist())
            base_url = st.text_input("Ingresa el URL base")

            if base_url:
                qr_data = []
                qr_images = []
                for index in range(start_row_index, len(df)):
                    params = {col: df.at[index, col] for col in selected_columns}
                    full_url = create_url(base_url, params)
                    qr_code = generate_qr(full_url)
                    qr_images.append(qr_code)
                    qr_data.append((params, full_url, qr_code))

                # Mostrar resultados en una tabla ordenada
                st.write("Resultados:")
                display_qr_table(qr_data)

                # Crear archivo ZIP y permitir la descarga
                zip_buffer = create_zip(qr_images)
                st.divider()
                st.download_button(label="Descargar todos los QR en un ZIP", data=zip_buffer, file_name="qr_codes.zip",
                                   mime="application/zip")