# Import the necessary libraries
import pandas as pd

import click

import gspread

# Google Sheets API scope and credentials
from google.oauth2.service_account import Credentials

SCOPE = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/drive.file'
]

CREDS = Credentials.from_service_account_file('creds.json')
SCOPED_CREDS = CREDS.with_scopes(SCOPE)
GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDS)

# @click.group decorator from click library
# This decorator is used to define a group of commands in a CLI application
@click.group()
def cli():
    # Placeholder that does nothing
    pass

@cli.command()
@click.argument('survey_results', type=str, help='Survey Results')
@click.argument('survey_results_output', type=str, help='CSV file for analyzing results')
def import_data(survey_results, survey_results_output):
    try:
        SHEET = GSPREAD_CLIENT.open('survey_results')
        results = SHEET.worksheet('results')
        data = results.get_all_values()
        # Getting the data for DataFrame without the headers
        dataframe = pd.DataFrame(data[1:], columns=data[0])
        # Save DataFrame to CSV file, excluding row index
        dataframe.to_csv(survey_results_output, index=False)
        print(f"Data imported from {survey_results} and exported to {survey_results_output}.")
    except Error as e:
        print(f"Error importing data from {str(e)}!")


# Converting the data to a Pandas Dataframe
dataframe = pd.DataFrame(data, columns=data[0])

# Calculate statistics
summary_statistics = dataframe.describe()

print(summary_statistics)

# Analyzing data
def analyze_data(data)