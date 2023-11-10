

col_to_keep = [
    'Name',
    'Created at',
    'Shipping City',
    'Shipping Name',
    'Shipping Phone',
    'Shipping Address1',
    'Lineitem name',
    'Lineitem quantity',
    'Lineitem price',
    'Total',
    'Currency',
       ]


rename_columns = {
    'Name': 'ID',
    'Created at': 'PURCHASED_DATE',
    'Shipping City': 'SHIPPING_CITY',
    'Shipping Name': 'CLIENT_NAME',
    'Shipping Phone': 'CLIENT_PHONE',
    'Shipping Address1': 'SHIPPING_ADDRESS',
    'Lineitem name': 'PRODUCT_NAME',
    'Lineitem quantity': 'PRODUCT_QUANTITY',
    'Lineitem price': 'PRODUCT_UNIT_PRICE',
    'Total': 'TOTAL',
    'Currency': 'CURRENCY',
}

cols_missing_phone_df = [
    "ID",
    "PURCHASED_DATE",
    "SHIPPING_CITY",
    "PRODUCT_NAME",
    "CLIENT_NAME"
]

msg_template = {
    "En stock": """Iaorana, ici Iaora Shopping !
Merci d'avoir passé commande pour le produit '{product}' 😊

Une livraison le {shipping_date} vous convient-elle ?

Merci de votre réponse !""",
    "Arrivage": """Iaorana, ici Iaora Shopping !
Le produit '{product}' à {product_price} {product_currency} est arrivé ! Si tu es dispo entre {city_1} et {city_2},
réponds OK à ce message.

ATTENTION: Nous ne pouvons pas recevoir d'appels sur ce numéro de téléphone, et ne répondons qu'aux SMS 
    """
}
