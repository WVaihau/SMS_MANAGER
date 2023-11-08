import streamlit_authenticator as stauth
import streamlit as st
import pandas as pd
import model as md
import qrcode
import io


def auth_usr() -> stauth.Authenticate:
    """Authenticate user."""
    config = st.secrets

    authenticator = stauth.Authenticate(
      dict(config.credentials),
      config.cookie.name,
      config.cookie.key,
      config.cookie.expiry_days,
      dict(config.preauthorized)
    )

    return authenticator


def process_df(df: pd.DataFrame) -> pd.DataFrame:
    """Process df"""
    # Filter DataFrame based on columns to keep
    filtered_df = df[md.col_to_keep]

    # Rename the columns
    filtered_df.rename(columns=md.rename_columns, inplace=True)

    filtered_df["CLIENT_PHONE"] = filtered_df["CLIENT_PHONE"].map(
      lambda phone: f"+{phone}")

    return filtered_df


@st.cache_data
def convert_df(df):
    """Convert df to csv for dowloading"""
    return df.to_csv().encode('utf-8')


@st.cache_data
def get_qr(text: str):
    """Get qrcode"""
    qr = qrcode.make(text)

    image_bytes = io.BytesIO()

    qr.save(image_bytes, format="PNG")
    return image_bytes


def csv_uploader(authenticator: stauth.Authenticate) -> pd.DataFrame:
    """Upload CSV."""

    st.title("Iaorana")

    uploaded_file = st.file_uploader(
      "Importer le fichier csv client",
      type=["csv"])

    if uploaded_file is not None:
        try:
            # Read CSV file into a Pandas DataFrame
            df = process_df(pd.read_csv(uploaded_file))
            st.success("Chargement du fichier client réussi")

            st.markdown("**Vue générale**")
            # Display the DataFrame
            st.dataframe(df)

            st.markdown("## Récupération des numéros clients pour livraisons")

            shipping_cities = st.multiselect(
              'Communes à desservir ?',
              df["SHIPPING_CITY"].unique(),
              ["Papeete"])

            if len(shipping_cities) != 0:
                filtered_df = df[df['SHIPPING_CITY'].isin(shipping_cities)]

                st.write(
                  "Données clients après applications des filtres: ",
                  filtered_df)

                phone_numbers = ", ".join(
                  filtered_df["CLIENT_PHONE"].unique().tolist())
                st.write("Liste des numéros clients:")
                st.code(phone_numbers)

                qrcode_svg = get_qr(phone_numbers)

                st.markdown("**Also get the list with this qrcode:**")
                left_co, cent_co, last_co = st.columns(3)
                with cent_co:
                    st.image(qrcode_svg, width=300)

                st.markdown("## Télécharger les fichiers")
                col1, col2 = st.columns(2)

                with col1:
                    st.download_button(
                      label="Download Raw Client Data",
                      data=convert_df(df),
                      file_name='raw_client_data.csv',
                      mime='text/csv')

                with col2:
                    st.download_button(
                      label="Download Filtered Client Data",
                      data=convert_df(filtered_df),
                      file_name='filtered_client_data.csv',
                      mime='text/csv')

            else:
                st.warning(
                  "Sélectionne au moins 1 colonne pour continuer..")

        except Exception as e:
            st.error(f"Error: {e}")

    c1, c2, c3 = st.columns(3)
    with c2:
        authenticator.logout('Se déconnecter', 'main')
