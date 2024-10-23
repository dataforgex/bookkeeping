import pandas as pd
import logging
from pathlib import Path
import re
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Function to get metadata for each file
def get_file_metadata(filepath):
    logging.debug(f"Getting metadata for file: {filepath}")
    stats = filepath.stat()
    return {
        'Size (Bytes)': stats.st_size,
        'Creation Time': pd.to_datetime(stats.st_ctime, unit='s'),
        'Modification Time': pd.to_datetime(stats.st_mtime, unit='s')
    }

# Function to extract amount and currency from file name
def extract_amount_and_currency(file_name):
    # Match pattern like xxx_yyy_dd where xxx is the name, yyy is the main amount, and dd is the decimal part or currency
    match = re.match(r'^[a-zA-Z]+_(\d+)(?:_(\d+))?(?:_(\d+|[a-zA-Z]+))?', file_name)
    if match:
        main_amount = match.group(1)
        decimal_amount = match.group(2)
        currency = match.group(3)

        # If there is a decimal part, combine it with the main amount
        if decimal_amount:
            amount = float(f"{main_amount}.{decimal_amount}")
        else:
            amount = float(main_amount)

        # Determine the currency
        if currency and not currency.isdigit():
            logging.info(f"Currency specified in file '{file_name}': {currency}")
            return amount, currency
        else:
            return amount, 'DKK'
    
    return None, None

# Function to read all file names and metadata from a given directory
def read_directory(directory_path):
    logging.info(f"Reading directory: {directory_path}")
    file_data = []
    
    # Traverse through all files in the directory
    for filepath in directory_path.rglob('*'):
        if filepath.is_file():
            logging.debug(f"Processing file: {filepath.name}")
            metadata = get_file_metadata(filepath)
            amount, currency = extract_amount_and_currency(filepath.name)
            
            # Append file information to the list
            file_data.append({
                'File Name': filepath.name,
                'Amount': amount,
                'Currency': currency,
                'File Path': str(filepath),
                **metadata
            })
    
    # Create a DataFrame with all collected file information
    df = pd.DataFrame(file_data)
    df['Currency'] = df['Currency'].where(df['Amount'].notna(), np.nan)
    logging.info("Finished reading directory and creating DataFrame")
    return df

if __name__ == "__main__":
    # Replace with your directory path
    directory_path = Path(r'/Volumes/DanExtDisk2/09')

    if not directory_path.exists() or not directory_path.is_dir():
        logging.error(f"The provided directory path does not exist or is not a directory: {directory_path}")
    else:
        logging.info("Starting the file metadata extraction process")
        
        # Read the directory and create the DataFrame
        df = read_directory(directory_path)
        
        # Display the DataFrame
        logging.info("Displaying the DataFrame")
        print(df)