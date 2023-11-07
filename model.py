

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
