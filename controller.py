from collections import Counter
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

    filtered_df["SHIPPING_CITY"] = filtered_df["SHIPPING_CITY"].map(
      lambda name: ''.join(name.split("'")))

    return filtered_df


def find_most_common_strings(string_list):
    """
    Finds the strings with the most occurrences in a list of strings.

    Args:
        string_list (list): A list of strings.

    Returns:
        list: A list containing the strings with the most
        occurrences in the input list.
    """
    # Count occurrences of each string in the list
    string_counts = Counter(string_list)

    # Find the highest number of occurrences
    max_occurrences = max(string_counts.values())

    # Find strings with the highest number of occurrences
    most_common_strings = [string for string, count in string_counts.items()
                           if count == max_occurrences]

    return most_common_strings


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

    st.title("Iaora Shopping 987")

    uploaded_file = st.file_uploader(
      "Importer le fichier csv client",
      type=["csv"])

    if uploaded_file is not None:
        try:
            # Read CSV file into a Pandas DataFrame
            df = process_df(pd.read_csv(uploaded_file, dtype=str))
            st.success("Chargement du fichier client réussi")

            st.markdown("**Vue générale**")
            # Display the DataFrame
            st.dataframe(df)

            st.markdown("## Récupération des numéros clients pour livraisons")

            cities = sorted(df["SHIPPING_CITY"].unique().tolist())
            shipping_cities = st.multiselect(
              'Communes à desservir ?',
              cities,
              find_most_common_strings(df["SHIPPING_CITY"].tolist()))

            products = sorted(df["PRODUCT_NAME"].unique().tolist())
            picked_products = st.multiselect(
              'Produits concernées ?',
              products,
              find_most_common_strings(df["PRODUCT_NAME"].tolist())
            )

            if len(shipping_cities) != 0 and len(picked_products) != 0:
                filtered_df = df[df['SHIPPING_CITY'].isin(shipping_cities)]
                filtered_df = filtered_df[
                    filtered_df['PRODUCT_NAME'].isin(picked_products)]

                st.write(
                  "Données clients après applications des filtres: ",
                  filtered_df)

                missing_phone_df = filtered_df[pd.isna(
                    filtered_df['CLIENT_PHONE'])]

                filtered_df = filtered_df[~pd.isna(
                    filtered_df['CLIENT_PHONE'])]

                phone_numbers = ", ".join(
                  filtered_df["CLIENT_PHONE"].unique().tolist())
                st.write("Liste des numéros clients:")
                st.code(phone_numbers)

                qrcode_svg = get_qr(phone_numbers)

                st.markdown("**Also get the list with this qrcode:**")
                _, cent_co, _ = st.columns(3)
                with cent_co:
                    st.image(qrcode_svg, width=300)

                if len(missing_phone_df) >= 1:
                    st.warning(
                        "Les personnes suivantes sont dans les communes"
                        " sélectionnées, mais n'ont pas donné de"
                        " numéro de téléphone: "
                        )
                    st.dataframe(
                        missing_phone_df[
                            ["ID",
                             "PURCHASED_DATE",
                             "SHIPPING_CITY",
                             "PRODUCT_NAME",
                             "CLIENT_NAME"]],
                        use_container_width=True,
                        hide_index=True)

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
                  "Sélectionne au moins 1 commune"
                  " et 1 produit pour continuer..")

        except Exception as e:
            st.error(f"Error: {e}")

    _, c2, _ = st.columns(3)
    with c2:
        authenticator.logout('Se déconnecter', 'main')
