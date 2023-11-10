import controller as ctrl
import streamlit as st

st.set_page_config(
    page_title="Iaora Shopping 987",
    page_icon="🇵🇫",
)


def main():

    authenticator = ctrl.auth_usr()

    name, authentication_status, username = authenticator.login(
        'Login', 'main')
    if st.session_state["authentication_status"]:
        with st.sidebar:
            st.header(f"🌴 {name}")
            df = ctrl.set_client_df()

        # Content
        st.title("🤙🏼 Iaora Shopping 987")

        if df is not None:
            _, lproducts = ctrl.get_variables(df)

            with st.sidebar:
                product = st.selectbox(
                    ':label: Produit concernée',
                    lproducts,
                    index=lproducts.index(
                        ctrl.find_most_common_strings(
                            df["PRODUCT_NAME"].tolist()
                        )[0]
                    ),
                    help="Le produit le plus demandé est sélectionné"
                    " par défaut"
                    )
                sub_df = df[df["PRODUCT_NAME"] == product]
                sub_df_nona = sub_df.dropna()
                product_price = sub_df_nona[
                    "PRODUCT_UNIT_PRICE"].unique().tolist()[0]
                product_currency = sub_df_nona["CURRENCY"].unique().tolist()[0]
                lcities = sub_df["SHIPPING_CITY"]
                sorted_lcities = ctrl.get_unique_list(
                    sub_df,
                    "SHIPPING_CITY",
                    unique=True,
                    sort=True
                    )

            with st.expander("**Fichier client brut**"):
                st.dataframe(
                    df,
                    hide_index=True,
                    use_container_width=True
                    )

            tab_phone, tab_msg = st.tabs(
                [
                    ":telephone_receiver: Phone numbers",
                    ":scroll: Messages"
                    ]
            )

            with tab_phone:
                cparams, coutput = st.columns(2)

                with cparams:
                    "### Parametrage"
                    cities = st.multiselect(
                        ':world_map: Communes à desservir',
                        sorted_lcities,
                        ctrl.find_most_common_strings(
                            lcities.tolist()),
                        help="La commune avec le plus de demande est"
                        " sélectionnée par défaut"
                    )
                    str_cities = ", ".join(cities)

                if len(cities) != 0 and len(product) != 0:
                    (
                        filtered_df,
                        phones_list,
                        phones_qrcode,
                        missing_phone_df) = ctrl.apply_filter(
                            sub_df,
                            cities)

                    with cparams:
                        "### Résumé"
                        "**Produit** :"
                        f"   - Nom :  {product}"
                        (
                            "   - Prix unitaire :"
                            f"  {product_price} {product_currency}")
                        f"**Communes à desservir**: {str_cities}"
                        (
                            "**Nombre de clients concernés**:"
                            f" {filtered_df.shape[0]}")

                    with coutput:
                        st.write("Liste des numéros clients:")
                        st.code(phones_list)

                        st.markdown("**Also get the list with this qrcode:**")
                        st.image(phones_qrcode, width=300)

                    if len(missing_phone_df) >= 1:
                        st.warning(
                            "Les personnes suivantes sont dans les "
                            "communes sélectionnées, mais n'ont pas"
                            " donné de numéro de téléphone: "
                            )
                        st.dataframe(
                            missing_phone_df,
                            use_container_width=True,
                            hide_index=True)

                    with st.expander("Fichier client avec les filtres"):
                        st.dataframe(
                            filtered_df.sort_values(by=["SHIPPING_CITY"]),
                            use_container_width=True,
                            hide_index=True
                        )
                else:
                    st.warning(
                        "Au moins une commune doit être sélectionner"
                        " pour continuer")

            with tab_msg:
                ltypes_msg = ctrl.get_msg_template()
                colparams, coloutput = st.columns(2)

                with colparams:
                    msg_type = st.selectbox(
                        ':speech_balloon: Type de message',
                        ltypes_msg.keys()
                    )
                msg_template = ltypes_msg[msg_type]
                if msg_type == "En stock":
                    with coloutput:
                        shipping_date = st.date_input(
                            ":calendar: Date de livraison", "today"
                        )
                    msg_text = msg_template.format(
                            product=product,
                            shipping_date=ctrl.format_date_french(
                                shipping_date))
                else:
                    with coloutput:
                        city_1 = st.selectbox(
                            ':city_sunrise: Commune de départ',
                            sorted_lcities
                            )
                        city_2 = st.selectbox(
                            ':city_sunset: Commune de fin',
                            sorted_lcities
                            )

                    msg_text = msg_template.format(
                        product=product,
                        product_price=product_price,
                        product_currency=product_currency,
                        city_1=city_1,
                        city_2=city_2
                    )
                if msg_type == "Arrivage":
                    if city_1 == city_2:
                        st.warning(
                            "Le segment de livraison est invalide. "
                            "Les deux pointent sur la même commune.")
                st.code(
                    msg_text
                )
                _, c2, _ = st.columns(3)
                msg_qrcode = ctrl.get_qr(msg_text)
                with c2:
                    st.image(msg_qrcode, width=200)
        else:
            st.warning("Ajouter le fichier client depuis la sidebar.")

        with st.sidebar:
            authenticator.logout('Se déconnecter', 'sidebar')
    elif st.session_state["authentication_status"] is False:
        st.error('Username/password is incorrect')
    elif st.session_state["authentication_status"] is None:
        st.warning('Please enter your username and password')


if __name__ == "__main__":
    main()
