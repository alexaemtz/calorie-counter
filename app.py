import streamlit as st
import os
from dotenv import load_dotenv
from PIL import Image
import google.generativeai as genai
import re

load_dotenv()
my_api_key = os.getenv("GOOGLE_API_KEY")

if not my_api_key:
    st.error("Por favor, configura la clave API de Google en las variables de entorno.")
else:
    genai.configure(api_key=my_api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")

    def input_image_details(image_upload):
        if image_upload is not None:
            bytes_data = image_upload.getvalue()
            image_parts = [{"mime_type": image_upload.type, "data": bytes_data}]
            return image_parts
        else:
            raise FileNotFoundError("No ha seleccionado una imagen.")

    def get_gemini_response(user_input, image, prompt):
        try:
            response = model.generate_content([user_input, image[0], prompt])
            return response
        except Exception as e:
            return f"Error al obtener la respuesta de Gemini: {e}"

    st.set_page_config(page_title="Calorie Counter", page_icon="🍵", layout="wide")
    st.title("🍵 Calorie Counter")
    st.write(
        """¡Bienvenido a Calorie Counter! Este proyecto te ayuda a calcular el número de calorías necesarias para una comida específica. 
        Utiliza el botón 'Subir imagen' para seleccionar una imagen y luego proporciona una descripción de la comida. 
        El sistema utilizará la inteligencia artificial de Gemini para calcular el número de calorías necesarias."""
    )

    user_input = st.text_input(
        "Ingrese una descripción de lo deseado:",
        placeholder="Ejemplo: Dime las calorías contenidas en este plato de ensalada.",
        key="user_input",
    )
    image_upload = st.file_uploader("Suba una imagen", type=["png", "jpg", "jpeg"])
    image = ""
    if image_upload is not None:
        image = Image.open(image_upload)
        st.image(image, caption="Imagen cargada", use_container_width=True)
    submit = st.button("Escanear la comida.")

    input_prompt = """ You are a helpful dietist. You must identy different types of food in images.
    The system should accurately detect and label varios foods displayed in the image, providing the name of the food.
    Additionally, the system should extract nutritional information and categorize the type of food (e.g., fruits, vegetables, grains, etc.) based on the detected items. 
    Include sugar contents, calories, protein, fat, carbohydrates, and fiber in the output. As well as if it's good for diabetics or not.
    Please provide the output in Spanish and in table format. 
    Also provide the total of sugar contents, calories, protein, fat, carbohydrates, and fiber in the output in a final row of the table. 
    """

    if submit:
        with st.spinner("Escaneando la comida..."):
            try:
                image_data = input_image_details(image_upload)
                response = get_gemini_response(input_prompt, image_data, user_input)

                # Extraer la tabla de la respuesta
                text_response = response.text
                table_match = re.search(r"\| Food Item.*\|", text_response, re.DOTALL)

                if table_match:
                    table_text = table_match.group(0)
                    lines = table_text.strip().split("\n")
                    headers = [h.strip() for h in lines[0].strip("|").split("|")]
                    data = []
                    for line in lines[2:]:
                        row = [r.strip() for r in line.strip("|").split("|")]
                        data.append(dict(zip(headers, row)))

                    st.subheader("Información Nutricional:")
                    st.table(data)
                else:
                    st.subheader("Resultados obtenidos: ")
                    st.write(response.text)

            except Exception as e:
                st.error(f"Ocurrió un error: {e}")