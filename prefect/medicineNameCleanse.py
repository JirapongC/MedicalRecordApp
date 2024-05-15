import os,textdistance, pandas as pd, psycopg2
from prefect import flow, task

postgresUser = os.getenv('POSTGRES_USER')
postgresPwd = os.getenv('POSTGRES_PASSWORD')
postgresHost = os.getenv('POSTGRES_HOST')
postgresDB = os.getenv('POSTGRES_DB')
postgresPort = os.getenv('POSTGRES_PORT')

@task
def medicineNameCleanseTask():
    conn = psycopg2.connect(host=postgresHost, database=postgresDB, user=postgresUser, password=postgresPwd)
    query = "SELECT * FROM health_link.prescription"
    df = pd.read_sql_query(query, conn)
    # Mockup medicine list
    medicineLlist = [
        "Ibuprofen",
        "Paracetamol",
        "Aspirin",
        "Acetaminophen",
        "Amoxicillin",
        "Levothyroxine",
        "Lisinopril",
        "Metformin",
        "Omeprazole",
        "Simvastatin",
        "Azithromycin",
        "Prednisone",
        "Atorvastatin",
        "Gabapentin",
        "Metoprolol",
        "Losartan",
        "Albuterol",
        "Citalopram",
        "Warfarin",
        "Fluoxetine"
    ]
    def updateMedicineName(inputMedicine, medicineMasterList):
        distances = [(med, textdistance.levenshtein.normalized_similarity(inputMedicine.lower(), med.lower())) for med in medicineMasterList] 
        closestMatch = max(distances, key=lambda x: x[1])
        return closestMatch[0]
    
    df['medicine_name'] = df['medicine_name'].apply(lambda x: updateMedicineName(x, medicineLlist))
    cur = conn.cursor()
    rows = zip(df.prescription_id, df.medicine_name)
    cur.execute("""CREATE TEMP TABLE temp_medicine_name_cleanse(prescription_id INTEGER, medicine_name VARCHAR) ON COMMIT DROP""")
    cur.executemany("""INSERT INTO temp_medicine_name_cleanse (prescription_id, medicine_name) VALUES(%s, %s)""", rows)
    cur.execute("""
        UPDATE health_link.prescription
        SET medicine_name = temp_medicine_name_cleanse.medicine_name
        FROM temp_medicine_name_cleanse
        WHERE temp_medicine_name_cleanse.prescription_id = prescription.prescription_id;
        """)
    conn.commit()
    cur.close()
    conn.close()

@flow(log_prints=True)
def medicineNameCleanseFlow():
    medicineNameCleanseTask()

if __name__ == "__main__":
    medicineNameCleanseFlow()