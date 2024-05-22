import os
from prefect import flow, task
from sling import Sling

@task
def importPatient():
    config = {
      'source': {
        'conn': "LOCAL",
        'stream': "file:///root/.prefect/sample_patient.csv"
      },
      'target': {
        'conn':  "APP_DB_CONNECTION",
        'object':  "medical_app.patient",
      },
      'mode': 'full-refresh'
    }
    Sling(**config).run()

@task
def importMedicalRecord():
    config = {
      'source': {
        'conn': "LOCAL",
        'stream': "file:///root/.prefect/sample_medical_record.csv"
      },
      'target': {
        'conn':  "APP_DB_CONNECTION",
        'object':  "medical_app.medical_record",
      },
      'mode': 'full-refresh'
    }
    Sling(**config).run()

@task
def importPrescription():
    config = {
      'source': {
        'conn': "LOCAL",
        'stream': "file:///root/.prefect/sample_prescription.csv"
      },
      'target': {
        'conn':  "APP_DB_CONNECTION",
        'object':  "medical_app.prescription",
      },
      'mode': 'full-refresh'
    }
    Sling(**config).run()

@flow(log_prints=True)
def initialAppData():
    importPatient()
    importMedicalRecord()
    importPrescription()

if __name__ == "__main__":
    initialAppData()
