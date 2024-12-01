import os
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import io
from PIL import Image

# Instellen van breed scherm en menu titel
st.set_page_config(layout="wide", page_title="Data App", page_icon="📊")

# Path to the logo
logo_path = os.path.join(os.getcwd(), "tkf_logo.png")

# Display the logo at the top of the app
st.sidebar.image(logo_path, use_column_width=True, caption="Bedrijfsnaam")




# Path to the Excel file
data_path = os.path.join(os.getcwd(), "Values.xlsx")

# Load existing data
try:
    data = pd.read_excel(data_path)
except FileNotFoundError:
    # Create een lege DataFrame als het bestand niet bestaat
    data = pd.DataFrame(columns=[
        "Datum",
        "Koper Trekolie Vetgehalte CU %",
        "Koper Gloeier Vetgehalte CU %",
        "Koper Trekolie pH Waarde",
        "Koper Gloeier pH Waarde",
        "Aluminum Trekolie Vetgehalte AL %",
        "Aluminum Gloeier Vetgehalte AL %",
        "Aluminum Trekolie pH Waarde",
        "Aluminum Gloeier pH Waarde"
    ])

# Normale bereiken voor de waarden
normal_ranges = {
    "Koper Trekolie Vetgehalte CU %": (14, 16),
    "Koper Gloeier Vetgehalte CU %": (1, 1.5),
    "Koper Trekolie pH Waarde": (8.5, 9),
    "Koper Gloeier pH Waarde": (8.5, 9),
    "Aluminum Trekolie Vetgehalte AL %": (22, 24),
    "Aluminum Gloeier Vetgehalte AL %": (3, 3.5),
    "Aluminum Trekolie pH Waarde": (8.5, 9),
    "Aluminum Gloeier pH Waarde": (8.5, 9),
}

# Sidebar menu with buttons
st.sidebar.title("Navigatie")
if st.sidebar.button("Data Entry"):
    menu = "Data Entry"
elif st.sidebar.button("Visualisatie"):
    menu = "Visualisatie"
else:
    menu = "Data Entry"  # Standaard pagina

# Data Entry Page
if menu == "Data Entry":
    st.title("Data Entry")
    col1, col2 = st.columns(2)

    with st.form("data_entry_form"):
        # Koper Columns
        with col1:
            st.subheader("Koper - Vetgehalte CU %")
            koper_trekolie_cu = st.number_input("Trekolie Vetgehalte CU %", step=0.1, format="%.2f", key="koper_trekolie_cu")
            koper_gloeier_cu = st.number_input("Gloeier Vetgehalte CU %", step=0.1, format="%.2f", key="koper_gloeier_cu")

            st.subheader("Koper - pH Waardes")
            koper_trekolie_ph = st.number_input("Trekolie pH Waarde", step=0.1, format="%.2f", key="koper_trekolie_ph")
            koper_gloeier_ph = st.number_input("Gloeier pH Waarde", step=0.1, format="%.2f", key="koper_gloeier_ph")

        # Aluminum Columns
        with col2:
            st.subheader("Aluminum - Vetgehalte AL %")
            aluminum_trekolie_al = st.number_input("Trekolie Vetgehalte AL %", step=0.1, format="%.2f", key="aluminum_trekolie_al")
            aluminum_gloeier_al = st.number_input("Gloeier Vetgehalte AL %", step=0.1, format="%.2f", key="aluminum_gloeier_al")

            st.subheader("Aluminum - pH Waardes")
            aluminum_trekolie_ph = st.number_input("Trekolie pH Waarde", step=0.1, format="%.2f", key="aluminum_trekolie_ph")
            aluminum_gloeier_ph = st.number_input("Gloeier pH Waarde", step=0.1, format="%.2f", key="aluminum_gloeier_ph")

        # Submit button
        submitted = st.form_submit_button("Submit")

    # Process the form submission
    if submitted:
        # Create a new row with the input values
        new_entry = {
            "Datum": [datetime.now().strftime("%Y-%m-%d")],  # Alleen datum opslaan
            "Koper Trekolie Vetgehalte CU %": [koper_trekolie_cu],
            "Koper Gloeier Vetgehalte CU %": [koper_gloeier_cu],
            "Koper Trekolie pH Waarde": [koper_trekolie_ph],
            "Koper Gloeier pH Waarde": [koper_gloeier_ph],
            "Aluminum Trekolie Vetgehalte AL %": [aluminum_trekolie_al],
            "Aluminum Gloeier Vetgehalte AL %": [aluminum_gloeier_al],
            "Aluminum Trekolie pH Waarde": [aluminum_trekolie_ph],
            "Aluminum Gloeier pH Waarde": [aluminum_gloeier_ph],
        }
        new_row = pd.DataFrame(new_entry)

        # Append the new row to the existing data
        data = pd.concat([data, new_row], ignore_index=True)

        # Save the updated data to Excel
        data.to_excel(data_path, index=False)
        st.success("Nieuwe gegevens succesvol toegevoegd!")

# Visualisatie Page
elif menu == "Visualisatie":
    st.title("Visualisatie van Data")

    if data.empty:
        st.warning("Geen gegevens beschikbaar om te visualiseren.")
    else:
        st.write("Hier zijn de grafieken voor de laatste 10 datapunten:")

        # Download knop voor alle data
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            data.to_excel(writer, index=False, sheet_name="Data")
        st.download_button(
            label="Download alle data",
            data=buffer,
            file_name="alle_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        # Laatste 10 datapunten
        data_subset = data.tail(10)

        # Velden voor de grafieken
        fields = list(normal_ranges.keys())

        # Maak een 2x4 layout voor de grafieken
        fig, axs = plt.subplots(2, 4, figsize=(16, 8))  # 2 rijen, 4 kolommen
        fig.subplots_adjust(hspace=0.5)  # Voeg ruimte toe tussen de grafieken

        axs = axs.flatten()  # Maak de assen array 1-dimensionaal

        for i, field in enumerate(fields):
            if field in data_subset.columns:
                y_min = min(data_subset[field].min() * 0.8, normal_ranges[field][0] * 0.8)  # 20% lager dan minimum
                y_max = max(data_subset[field].max() * 1.2, normal_ranges[field][1] * 1.2)  # 20% hoger dan maximum
                axs[i].plot(data_subset["Datum"], data_subset[field], marker="o", linestyle="-")
                axs[i].fill_between(
                    data_subset["Datum"],
                    normal_ranges[field][0],
                    normal_ranges[field][1],
                    color="lightblue",
                    alpha=0.3,
                )
                axs[i].set_title(field)
                axs[i].set_xlabel("Datum")
                axs[i].set_ylabel("Waarde")
                axs[i].set_xticks(range(0, len(data_subset), max(1, len(data_subset) // 6)))  # Toon elke 6e datum
                axs[i].set_xticklabels(data_subset["Datum"].iloc[::max(1, len(data_subset) // 6)], rotation=45)
                axs[i].set_ylim(y_min, y_max)

        # Verwijder lege subplots
        for j in range(len(fields), len(axs)):
            fig.delaxes(axs[j])

        st.pyplot(fig)
