import pandas as pd
import os

input_file_path = 'data/data.xlsx'
output_folder_path = 'cleanedData'
output_file_path = os.path.join(output_folder_path, 'data.csv')

def convert_excel_to_csv():
    """
    Reads an Excel file and converts it to a CSV file.
    """
    if not os.path.exists(input_file_path):
        print(f"Error: Input file not found at '{input_file_path}'")
        return

    os.makedirs(output_folder_path, exist_ok=True)

    try:
        df = pd.read_excel(input_file_path)

        df.to_csv(output_file_path, index=False)

        print(f"Successfully converted '{input_file_path}' to '{output_file_path}'")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    convert_excel_to_csv()