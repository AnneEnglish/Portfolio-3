# Import the necessary libraries
import pandas as pd
import click
import gspread

# Google Sheets API Credentias and Scope
from google.oauth2.service_account import Credentials

SCOPE = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/drive.file'
]
CREDS = Credentials.from_service_account_file('creds.json')
SCOPED_CREDS = CREDS.with_scopes(SCOPE)
GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDS)


def import_data(survey_results):
    """
    This function gets the survey data by sheet name.
    It then returns that data as a Pandas DataFrame
    """
    try:
        sheet = GSPREAD_CLIENT.open('survey_results')
        worksheet = sheet.get_worksheet(0)
        survey_data = worksheet.get_all_records()
        return pd.DataFrame(survey_data)
    except Exception as e:
        raise click.ClickException(f"Error importing data: {str(e)}")


def analyze_data(df):
    """
    This function analyzes the survey data.
    """
    print(df.describe())
    print(df['Age'].value_counts())


# Click command to run the analysis
@click.command()
@click.option('--survey_results', prompt='Enter Google Sheet name', help='Name of sheet containing survey data')
def analyze(survey_results):
    df = import_data(survey_results)


if __name__ == '__main__':
    analyze()
    