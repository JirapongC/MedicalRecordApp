import os
from prefect import flow, task
from prefect_shell import ShellOperation
from sling import Sling

appPostgresUser = os.getenv('APP_POSTGRES_USER')
appPostgresPwd = os.getenv('APP_POSTGRES_PASSWORD')
appPostgresHost = os.getenv('APP_POSTGRES_HOST')
appPostgresDB = os.getenv('APP_POSTGRES_DB')
appPostgresPort = os.getenv('APP_POSTGRES_PORT')

analyticPostgresUser = os.getenv('ANALYTIC_POSTGRES_USER')
analyticPostgresPwd = os.getenv('ANALYTIC_POSTGRES_PASSWORD')
analyticPostgresHost = os.getenv('ANALYTIC_POSTGRES_HOST')
analyticPostgresDB = os.getenv('ANALYTIC_POSTGRES_DB')
analyticPostgresPort = os.getenv('ANALYTIC_POSTGRES_PORT')

appCommand='PGPASSWORD='+appPostgresPwd+' psql -h '+appPostgresHost+' -U '+appPostgresUser+' -d '+appPostgresDB+' '
analyticCommand='PGPASSWORD='+analyticPostgresPwd+' psql -h '+analyticPostgresHost+' -U '+analyticPostgresUser+' -d '+analyticPostgresDB+' '

@task
def loadSTGPatient():
    config = {
      'source': {
        'conn': 'APP_DB_CONNECTION',
        'stream': "medical_app.patient",
      },
      'target': {
        'conn':  "ANALYTIC_DB_CONNECTION",
        'object':  "stg.stg_patient",
      },
      'mode': 'full-refresh'
    }
    Sling(**config).run()

@task
def loadSTGMedicalRecord():
    config = {
      'source': {
        'conn': 'APP_DB_CONNECTION',
        'stream': "medical_app.medical_record",
      },
      'target': {
        'conn':  "ANALYTIC_DB_CONNECTION",
        'object':  "stg.stg_medical_record",
      },
      'mode': 'full-refresh'
    }
    Sling(**config).run()

@task
def loadSTGPrescription():
    config = {
      'source': {
        'conn': 'APP_DB_CONNECTION',
        'stream': "medical_app.prescription",
      },
      'target': {
        'conn':  "ANALYTIC_DB_CONNECTION",
        'object':  "stg.stg_prescription",
      },
      'mode': 'full-refresh'
    }
    Sling(**config).run()

@task
def populateMedicalRecordDenormalized():
    with ShellOperation(
    commands=[
        analyticCommand + ''' -f /root/.prefect/mergeMedicalRecordDenormalized.sql'''
        ],
       ) as PSQLCommand:
        PSQLCommand = PSQLCommand.trigger()
        PSQLCommand.wait_for_completion()
        PSQLOutput = PSQLCommand.fetch_result()
        print(PSQLOutput)

@flow(log_prints=True)
def loadAnalyticDB():
    loadSTGPatient()
    loadSTGMedicalRecord()
    loadSTGPrescription()
    populateMedicalRecordDenormalized()

if __name__ == "__main__":
    loadAnalyticDB()
