import os, psycopg2
from prefect import flow, task
from prefect_shell import ShellOperation

postgresUser = os.getenv('APP_POSTGRES_USER')
postgresPwd = os.getenv('APP_POSTGRES_PASSWORD')
postgresHost = os.getenv('APP_POSTGRES_HOST')
postgresDB = os.getenv('APP_POSTGRES_DB')
postgresPort = os.getenv('APP_POSTGRES_PORT')
command='PGPASSWORD='+postgresPwd+' psql -h '+postgresHost+' -U '+postgresUser+' -d '+postgresDB+' '
@task
def truncatePatient():
    with ShellOperation(commands=[command + '''-c "truncate table medical_app.patient;"'''
                                  ,command + '''-c "alter sequence medical_app.patient_patient_id_seq restart with 1;"'''
                                  ],) as PSQLCommand:
        PSQLCommand = PSQLCommand.trigger()
        PSQLCommand.wait_for_completion()
        PSQLOutput = PSQLCommand.fetch_result()
        print(PSQLOutput)

@task
def truncateMedicalRecord():
    with ShellOperation(commands=[command + '''-c "truncate table medical_app.medical_record;"'''
                                  ,command + '''-c "alter sequence medical_app.medical_record_medical_record_id_seq restart with 1;"'''
                                  ],) as PSQLCommand:
        PSQLCommand = PSQLCommand.trigger()
        PSQLCommand.wait_for_completion()
        PSQLOutput = PSQLCommand.fetch_result()
        print(PSQLOutput)

@task
def truncatePrescription():
    with ShellOperation(commands=[command + '''-c "truncate table medical_app.prescription;"'''
                                  ,command + '''-c "alter sequence medical_app.prescription_prescription_id_seq restart with 1;"'''
                                  ],) as PSQLCommand:
        PSQLCommand = PSQLCommand.trigger()
        PSQLCommand.wait_for_completion()
        PSQLOutput = PSQLCommand.fetch_result()
        print(PSQLOutput)

@task
def importPatient():
    with ShellOperation(
    commands=[command + '''-c "\COPY medical_app.patient (id_card_num,first_name,last_name,birth_date,phone_num)FROM '/root/.prefect/sample_patient.csv' WITH CSV HEADER;"'''],) as PSQLCommand:
        PSQLCommand = PSQLCommand.trigger()
        PSQLCommand.wait_for_completion()
        PSQLOutput = PSQLCommand.fetch_result()
        print(PSQLOutput)

@task
def importMedicalRecord():
    with ShellOperation(
    commands=[command + '''-c "\COPY medical_app.medical_record (patient_id,hospital_name,doctor_full_name,diagnosis,symtom,treatment_start_date,treatment_end_date)FROM '/root/.prefect/sample_medical_record.csv' WITH CSV HEADER;"'''],) as PSQLCommand:
        PSQLCommand = PSQLCommand.trigger()
        PSQLCommand.wait_for_completion()
        PSQLOutput = PSQLCommand.fetch_result()
        print(PSQLOutput)

@task
def importPrescription():
    with ShellOperation(commands=[command + '''-c "\COPY medical_app.prescription (medical_record_id,medicine_name,dose)FROM '/root/.prefect/sample_prescription.csv' WITH CSV HEADER;"'''],) as PSQLCommand:
        PSQLCommand = PSQLCommand.trigger()
        PSQLCommand.wait_for_completion()
        PSQLOutput = PSQLCommand.fetch_result()
        print(PSQLOutput)

@flow(log_prints=True)
def initializeAppData():
    truncatePatient()
    truncateMedicalRecord()
    truncatePrescription()
    importPatient()
    importMedicalRecord()
    importPrescription()

if __name__ == "__main__":
    initializeAppData()
