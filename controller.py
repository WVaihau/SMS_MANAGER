from collections import Counter
from datetime import datetime
import io
import model as md
import pandas as pd
import qrcode
import streamlit_authenticator as stauth
import streamlit as st


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


def get_today_date():
    """Return today date."""
    return datetime.now()


def get_msg_template():
    """Return message template."""
    return md.msg_template


def process_df(df: pd.DataFrame) -> pd.DataFrame:
    """Process df"""
    # Filter DataFrame based on columns to keep
    filtered_df = df[md.col_to_keep]

    # Rename the columns
    filtered_df.rename(columns=md.rename_columns, inplace=True)

    df_with_any_na = filtered_df[filtered_df.isna().any(axis=1)]

    filtered_df = filtered_df.dropna(
        subset=['SHIPPING_CITY'])

    filtered_df["SHIPPING_CITY"] = filtered_df["SHIPPING_CITY"].map(
      lambda name: ''.join(name.split("'")))

    return filtered_df, df_with_any_na


def parse_phone_number(df: pd.DataFrame) -> str:
    """Parse phone numbers"""
    phone_numbers = ", ".join(df["CLIENT_PHONE"].unique().tolist())

    parsed_phone_numbers = st.secrets.phones.template.format(
        phone_numbers=phone_numbers
    )

    return parsed_phone_numbers


def apply_filter(
        p_df: pd.DataFrame,
        cities: list) -> pd.DataFrame:
    """Apply filter on given df."""
    df = p_df.copy(deep=True)

    df = df[df["SHIPPING_CITY"].isin(cities)]

    raw_missing_phone_df = df[pd.isna(df["CLIENT_PHONE"])]
    missing_phone_df = raw_missing_phone_df[md.cols_missing_phone_df]

    df_nona = df[~pd.isna(df['CLIENT_PHONE'])]
    parsed_phones = parse_phone_number(df_nona)

    parsed_phones_qrcode = get_qr(f"{parsed_phones}")

    return df, parsed_phones, parsed_phones_qrcode, missing_phone_df


def format_date_french(date):
    months = [
        "janvier", "février", "mars", "avril", "mai", "juin",
        "juillet", "août", "septembre", "octobre", "novembre", "décembre"
    ]

    days = [
        "lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"
    ]

    rday_of_week = days[date.weekday()]
    day_of_week = rday_of_week[0].upper() + rday_of_week[1:]
    day_number = date.day
    month = months[date.month - 1]  # Month index starts from 1
    year = date.year

    formatted_date = f"{day_of_week} {day_number} {month} {year}"
    return formatted_date


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

    return sorted(most_common_strings)


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


def get_unique_list(
        df: pd.DataFrame,
        col: str,
        unique: bool = False,
        sort: bool = True) -> list:
    """Get unique list from 'col' in 'df'"""
    values = df.copy(deep=True)[col]

    if unique:
        values = values.unique()

    values = values.tolist()

    if sort:
        values = sorted(values)

    return values


def get_variables(df: pd.DataFrame) -> list:
    """Variables based on client file."""
    return (
        get_unique_list(
            df,
            "SHIPPING_CITY",
            unique=True,
            sort=True
        ),
        get_unique_list(
            df,
            "PRODUCT_NAME",
            unique=True,
            sort=True
        )
    )


def set_client_df() -> pd.DataFrame:
    """Get client dataframe."""

    file = st.file_uploader(
        "📂 Importer le fichier client",
        type=["csv"]
    )

    if file is not None:
        return process_df(pd.read_csv(file, dtype=str))
    else:
        return None
