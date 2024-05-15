import os
from prefect import flow, task
from prefect_shell import ShellOperation

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
def exportPatient():
    with ShellOperation(
    commands=[appCommand + '''-c "\copy (SELECT * FROM medical_app.patient) TO '/root/.prefect/patient.csv' WITH CSV HEADER;"'''],
    ) as PSQLCommand:
        PSQLCommand = PSQLCommand.trigger()
        PSQLCommand.wait_for_completion()
        PSQLOutput = PSQLCommand.fetch_result()
        print(PSQLOutput)

@task
def exportMedicalRecord():
    with ShellOperation(
    commands=[appCommand + ''' -c "\copy (SELECT * FROM medical_app.medical_record) TO '/root/.prefect/medicalRecord.csv' WITH CSV HEADER;"'''],
    ) as PSQLCommand:
        PSQLCommand = PSQLCommand.trigger()
        PSQLCommand.wait_for_completion()
        PSQLOutput = PSQLCommand.fetch_result()
        print(PSQLOutput)

@task
def exportPrescription():
    with ShellOperation(
    commands=[appCommand + ''' -c "\copy (SELECT * FROM medical_app.prescription) TO '/root/.prefect/prescription.csv' WITH CSV HEADER;"'''],
    ) as PSQLCommand:
        PSQLCommand = PSQLCommand.trigger()
        PSQLCommand.wait_for_completion()
        PSQLOutput = PSQLCommand.fetch_result()
        print(PSQLOutput)

@task
def loadAnalyticSTGPatient():
    with ShellOperation(
    commands=[
        analyticCommand + ''' -c "truncate table stg.stg_patient;"'''
        ,analyticCommand + ''' -c "\copy stg.stg_patient FROM '/root/.prefect/patient.csv' WITH CSV HEADER;"'''
        ],
       ) as PSQLCommand:
        PSQLCommand = PSQLCommand.trigger()
        PSQLCommand.wait_for_completion()
        PSQLOutput = PSQLCommand.fetch_result()
        print(PSQLOutput)

@task
def loadAnalyticSTGMedicalRecord():
    with ShellOperation(
    commands=[
        analyticCommand + ''' -c "truncate table stg.stg_medical_record;"'''
        ,analyticCommand + ''' -c "\copy stg.stg_medical_record FROM '/root/.prefect/medicalRecord.csv' WITH CSV HEADER;"'''
        ],
       ) as PSQLCommand:
        PSQLCommand = PSQLCommand.trigger()
        PSQLCommand.wait_for_completion()
        PSQLOutput = PSQLCommand.fetch_result()
        print(PSQLOutput)

@task
def loadAnalyticSTGPrescription():
    with ShellOperation(
    commands=[
        analyticCommand + ''' -c "truncate table stg.stg_prescription;"'''
        ,analyticCommand + ''' -c "\copy stg.stg_prescription FROM '/root/.prefect/prescription.csv' WITH CSV HEADER;"'''
        ],
       ) as PSQLCommand:
        PSQLCommand = PSQLCommand.trigger()
        PSQLCommand.wait_for_completion()
        PSQLOutput = PSQLCommand.fetch_result()
        print(PSQLOutput)

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
    exportPatient()
    exportMedicalRecord()
    exportPrescription()
    loadAnalyticSTGPatient()
    loadAnalyticSTGMedicalRecord()
    loadAnalyticSTGPrescription()
    populateMedicalRecordDenormalized()

if __name__ == "__main__":
    loadAnalyticDB()
