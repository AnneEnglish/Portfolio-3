# Import the necessary libraries
import os
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
    This function imports data from a Google Sheet.
    It then returns that data as a Pandas DataFrame.

    Args: 
        survey_results (str): The name of the Google Sheet
    
    Returns:
        pd.DataFrame: The survey data as Pandas DataFrame.
    """
    if not survey_results:
        raise ValueError('survey_results cannot be empty.')

    try:
        sheet = GSPREAD_CLIENT.open(survey_results)
        worksheet = sheet.get_worksheet(0)
        survey_data = worksheet.get_all_records()
        return pd.DataFrame(survey_data)
    except Exception as e:
        raise click.ClickException(f"Error importing data: {str(e)}")


def analyze_data(df):
    """
    Function to analyze data and provide insights.

    Args:
        df (pd.DataFrame): The survey data as Pandas DataFrame.
    
    Returns:
        None
    """
    if df.empty:
        raise ValueError('The DataFrame is empty.')

    required_columns = ['Do you feel focused in class?',
                        'Please select your gender below:',
                        'What do you use to study primarily?'
                        ]

    for column in required_columns:
        if column not in df.columns:
            raise ValueError("The column '{column}' is not in DataFrame")

    total_participants = len(df)

    try:
        # Calculate the % of participants who feel focused in class
        focused = df['Do you feel focused in class?'] \
            .str.lower().str.count('yes').sum()
        focused_percentage = (focused / total_participants) * 100
    except ZeroDivisionError:
        focused_percentage = 0

    try:
        # Calculate the % of participants that are male
        male_participants = df['Please select your gender below:'] \
            .str.lower().str.count('male').sum()
        male_percentage = (male_participants / total_participants) * 100
    except ZeroDivisionError:
        male_percentage = 0

    try:
        # Calculate the % of participants that are female
        female_participants = df['Please select your gender below:'] \
            .str.lower().str.count('female').sum()
        female_percentage = (female_participants / total_participants) * 100
    except ZeroDivisionError:
        female_percentage = 0

    # Get the preferred method of study
    study_method = df['What do you use to study primarily?'].mode().values[0]
    try:
        # Calculate the % of people that prefer the most common study method
        study_method_count = len(df[df['What do you use to study primarily?']
                                    == study_method])
        study_method_percent = (study_method_count / total_participants) * 100
    except ZeroDivisionError:
        study_method_percent = 0

    # Print statements to display the output of calculations above
    print('Number of participants:', total_participants)
    print(df['Please select your age range below:'].value_counts())
    print(f'Percentage of male participants: {male_percentage:.2f}%')
    print(f'Percentage of female participants: {female_percentage:.2f}%')
    print(f'Percentage of people that feel focused: {focused_percentage:.2f}%')
    print(f'Most common study method: {study_method}')
    # Print statement split into two lines for readability
    print('Percentage of people that prefer the most common study method: ',
          end='')
    print(f'{study_method_percent:.2f}%')


def export_data(df, output_file):
    """
    Function to export analyzed data to a CSV file.

    Args:
        df (pd.DataFrame): The survey data as Pandas DataFrame
        output_file (str): The name of the output file.

    Returns:
        None
    """
    if not output_file:
        raise ValueError('output_file cannot be empty')

    try:
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        df.to_csv(output_file, index=False)
        print(f'Data exported to: {output_file}')
    except Exception as e:
        print(f'Error exporting data: {str(e)}')


# Click command to run the analysis
@click.command()
@click.option(
    '--survey_results',
    prompt='Enter Sheet name',
    help='Survey data sheet name'
)
@click.option(
    '--output_csv',
    default='survey_data_output.csv',
    help='Output CSV filename'
)
def analyze(survey_results, output_csv):
    """
    This function runs the analysis of the survey data.

    Args: 
        survey_results (str): The name of the Google Sheet.
        output_csv (str): The name of the output CSV file.

    Returns:
        None
    """
    if survey_results != 'survey_results':
        print('Error: Invalid sheet name! Enter the correct sheet name.')
        return

    try:
        df = import_data(survey_results)
        analyze_data(df)

        # CSV output file path
        output_csv = os.path.join(os.getcwd(), 'survey_data_output.csv')
        export_data(df, output_csv)
    except Exception as e:
        print(f'Error: {str(e)}')


# pylint: disable=no-value-for-parameter
if __name__ == '__main__':
    analyze()
