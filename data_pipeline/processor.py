def clean_and_process_data(raw_data):
    import pandas as pd
    try:
        from .config import CURRENCY_CONVERSION_RATE
    except ImportError:
        from config import CURRENCY_CONVERSION_RATE

    # Convert raw data to DataFrame
    df = pd.DataFrame(raw_data)

    # Clean and process data
    # Example: Convert price to float and handle missing values
    df['price'] = df['price'].astype(str).str.replace('£', '', regex=False).astype(float)
    df['availability'] = df['availability'].str.strip()

    # Median imputation for missing values in 'price'
    df['price'] = df['price'].fillna(df['price'].median())

    # Currency conversion (1 GBP = 105.50 INR)
    df['price_in_inr'] = df['price'] * CURRENCY_CONVERSION_RATE

    return df


def clean_data(raw_data):
    records = clean_and_process_data(raw_data).to_dict(orient='records')
    for record in records:
        record['price'] = record.pop('price_in_inr')
    return records


def process_books(raw_data):
    return clean_data(raw_data)

def validate_data(df):
    # Validate the cleaned data
    if df.isnull().values.any():
        raise ValueError("Data contains missing values after processing.")
    if df['price'].min() < 0:
        raise ValueError("Price cannot be negative.")
    
    return True