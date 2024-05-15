import os
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

postgresUser = os.getenv('POSTGRES_USER')
postgresPwd = os.getenv('POSTGRES_PASSWORD')
postgresHost = os.getenv('POSTGRES_HOST')
postgresDB = os.getenv('POSTGRES_DB')
postgresPort = os.getenv('POSTGRES_PORT')
SQLAlchemyDBURI = 'postgresql://'+postgresUser+':'+postgresPwd+'@'+postgresHost+':'+postgresPort+'/'+postgresDB

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = SQLAlchemyDBURI
app.json.sort_keys = False

db = SQLAlchemy(app)

class Patient(db.Model):
    __tablename__ = 'patient'
    __table_args__ = {'schema': 'medical_app'}

    patient_id = db.Column(db.Integer, primary_key=True)
    id_card_num = db.Column(db.String(13))
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    birth_date = db.Column(db.Date)
    phone_num = db.Column(db.String(10))
    inserted_timestamp = db.Column(db.DateTime)
    updated_timestamp = db.Column(db.DateTime)

    def __repr__(self):
        return '<Patient %r>' % self.name

class MedicalRecord(db.Model):
    __tablename__ = 'medical_record'
    __table_args__ = {'schema': 'medical_app'}

    medical_record_id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer)
    hospital_name = db.Column(db.String(50))
    doctor_full_name = db.Column(db.String(50))
    diagnosis = db.Column(db.String(255))
    symtom = db.Column(db.String(255))
    treatment_start_date = db.Column(db.Date)
    treatment_end_date = db.Column(db.Date)
    inserted_timestamp = db.Column(db.DateTime)
    updated_timestamp = db.Column(db.DateTime)

    def __repr__(self):
        return '<MedicalRecord %r>' % self.name

class Prescription(db.Model):
    __tablename__ = 'prescription'
    __table_args__ = {'schema': 'medical_app'}

    prescription_id = db.Column(db.Integer, primary_key=True)
    medical_record_id = db.Column(db.Integer)
    medicine_name = db.Column(db.String(50))
    dose = db.Column(db.String(50))
    inserted_timestamp = db.Column(db.DateTime)
    updated_timestamp = db.Column(db.DateTime)

    def __repr__(self):
        return '<Prescription %r>' % self.name

@app.route("/patient",methods= ["GET"])
def getPatients():
    patients = Patient.query.all()
    output = []
    for patient in patients:
        patientData = {'patientID': patient.patient_id
                        ,'idCardNum': patient.id_card_num
                        ,'firstName': patient.first_name
                        ,'lastName': patient.last_name
                        ,'birthDate': patient.birth_date.strftime('%Y-%m-%d') if patient.birth_date else ""
                        ,'phoneNum': patient.phone_num
                        }
        output.append(patientData)
    return jsonify({'patients': output})

@app.route('/patient/<idCardNum>', methods=['GET'])
def getPatientByIDCard(idCardNum):
    patient = Patient.query.filter_by(id_card_num=idCardNum).first()
    if not patient:
        return jsonify({'error': 'Patient not found'}), 404
    patientData = {'patientID': patient.patient_id
                    ,'idCardNum': patient.id_card_num
                    ,'firstName': patient.first_name
                    ,'lastName': patient.last_name
                    ,'birthDate': patient.birth_date.strftime('%Y-%m-%d') if patient.birth_date else ""
                    ,'phoneNum': patient.phone_num
                    }
    return jsonify({'patient': patientData})

@app.route('/patient', methods=['POST'])
def addPatient():
    data = request.get_json()
    idCardNum = data.get('idCardNum')
    if Patient.query.filter_by(id_card_num=idCardNum).first():
        return jsonify({'error': 'Patient with id_card_num already exists'}), 400
    
    newPatient = Patient(id_card_num=data['idCardNum']
                         ,first_name=data['firstName']
                         ,last_name=data['lastName']
                         ,birth_date=data['birthDate']
                         ,phone_num=data['phoneNum']
                        )
    newPatient.inserted_timestamp = datetime.now()+ timedelta(hours=7)
    db.session.add(newPatient)
    db.session.commit()
    return jsonify({'message': 'Patient registered successfully'}), 201

@app.route("/patient/<patientID>", methods=["PUT"])
def updatePatient(patientID):
    data = request.json
    idCardNum = data.get('idCardNum')
    patient = Patient.query.filter_by(patient_id=patientID).first()
    if not patient:
        return jsonify({'error': 'Patient not found'}), 404
    if patient.id_card_num != idCardNum:
        idCardNumValidation = Patient.query.filter_by(id_card_num=idCardNum).first()
        if idCardNumValidation:
            return jsonify({'error': 'Patient with id_card_num already exists'}), 400

    patient.id_card_num = data.get('idCardNum', patient.id_card_num)
    patient.first_name = data.get('firstName', patient.first_name)
    patient.last_name = data.get('lastName', patient.last_name)
    patient.birth_date = data.get('birthDate', patient.birth_date)
    patient.phone_num = data.get('phoneNum', patient.phone_num)
    patient.updated_timestamp = datetime.now()+ timedelta(hours=7)
    db.session.commit()
    return jsonify({'message': 'Patient updated successfully'})

@app.route("/patient/<patientID>", methods=["DELETE"])
def deletePatient(patientID):
    patient = Patient.query.filter_by(patient_id=patientID).first()
    if not patient:
        return jsonify({'error': 'Patient not found'}), 404
    db.session.delete(patient)
    db.session.commit()
    return jsonify({'message': 'Patient deleted successfully'})
    
@app.route("/medicalrecord",methods= ["GET"])
def getMedicalRecords():
    medicalRecords = MedicalRecord.query.all()
    output = []
    for medicalRecord in medicalRecords:
        data = {
                'medicalRecordID': medicalRecord.medical_record_id
                ,'patientID': medicalRecord.patient_id
                ,'hospitalName': medicalRecord.hospital_name
                ,'doctorFullName': medicalRecord.doctor_full_name
                ,'diagnosis': medicalRecord.diagnosis
                ,'symtom': medicalRecord.symtom
                ,'treatmentStartDate': medicalRecord.treatment_start_date.strftime('%Y-%m-%d') if medicalRecord.treatment_start_date else ""
                ,'treatmentEndDate': medicalRecord.treatment_end_date.strftime('%Y-%m-%d') if medicalRecord.treatment_end_date else ""
                }
        output.append(data)
    return jsonify({'medicalRecords': output})

@app.route("/medicalrecord/<int:patientID>",methods= ["GET"])
def getMedicalRecordsByPatientID(patientID):
    medicalRecords = MedicalRecord.query.filter_by(patient_id=patientID).all()
    if not medicalRecords:
        return jsonify({'error': 'Medical record not found for patient'}), 404
    output = []
    for medicalRecord in medicalRecords:
        data = {
                'medicalRecordID': medicalRecord.medical_record_id
                ,'patientID': medicalRecord.patient_id
                ,'hospitalName': medicalRecord.hospital_name
                ,'doctorFullName': medicalRecord.doctor_full_name
                ,'diagnosis': medicalRecord.diagnosis
                ,'symtom': medicalRecord.symtom
                ,'treatmentStartDate': medicalRecord.treatment_start_date.strftime('%Y-%m-%d') if medicalRecord.treatment_start_date else ""
                ,'treatmentEndDate': medicalRecord.treatment_end_date.strftime('%Y-%m-%d') if medicalRecord.treatment_end_date else ""
                }
        output.append(data)
    return jsonify({'medicalRecords': output})

@app.route("/medicalrecord", methods=["POST"])
def createMedicalRecord():
    data = request.json
    patientID = data.get('patientID')
    patient = Patient.query.filter_by(patient_id=patientID).first()
    if not patient:
        return jsonify({'error': 'Patient not found'}), 404
    newRecord = MedicalRecord(
        patient_id=data['patientID'],
        hospital_name=data['hospitalName'],
        doctor_full_name=data['doctorFullName'],
        diagnosis=data['diagnosis'],
        symtom=data['symtom'],
        treatment_start_date=datetime.strptime(data['treatmentStartDate'], '%Y-%m-%d'),
        treatment_end_date=datetime.strptime(data['treatmentEndDate'], '%Y-%m-%d')
    )
    newRecord.inserted_timestamp = datetime.now()+ timedelta(hours=7)
    db.session.add(newRecord)
    db.session.commit()
    return jsonify({'message': 'Medical record added successfully'}), 201

@app.route("/medicalrecord/<int:medicalRecordID>", methods=["PUT"])
def updateMedicalRecord(medicalRecordID):
    data = request.json
    record = MedicalRecord.query.get(medicalRecordID)
    if not record:
        return jsonify({'error': 'Medical record not found'}), 404
    record.patient_id = data.get('patientID', record.patient_id)
    record.hospital_name = data.get('hospitalName', record.hospital_name)
    record.doctor_full_name = data.get('doctorFullName', record.doctor_full_name)
    record.diagnosis = data.get('diagnosis', record.diagnosis)
    record.symtom = data.get('symtom', record.symtom)
    record.treatment_start_date = datetime.strptime(data['treatmentStartDate'], '%Y-%m-%d') 
    record.treatment_end_date = datetime.strptime(data['treatmentEndDate'], '%Y-%m-%d')
    record.updated_timestamp = datetime.now()+ timedelta(hours=7)

    db.session.commit()
    return jsonify({'message': 'Medical record updated successfully'})

@app.route("/medicalrecord/<int:medicalRecordID>", methods=["DELETE"])
def deleteMedicalRecord(medicalRecordID):
    record = MedicalRecord.query.get(medicalRecordID)
    if not record:
        return jsonify({'error': 'Medical record not found'}), 404
    db.session.delete(record)
    db.session.commit()
    return jsonify({'message': 'Medical record deleted successfully'})

@app.route("/prescription",methods= ["GET"])
def getPrescriptions():
    prescriptions = Prescription.query.all()
    output = []
    for prescription in prescriptions:
        prescriptionData = {'prescriptionID': prescription.prescription_id
                        ,'medicalRecordID': prescription.medical_record_id
                        ,'medicineName': prescription.medicine_name
                        ,'dose': prescription.dose
                        }
        output.append(prescriptionData)
    return jsonify({'prescriptions': output})

@app.route("/prescription/<int:medicalRecordID>",methods= ["GET"])
def getPrescriptionsByMedicalRecordID(medicalRecordID):
    prescriptions = Prescription.query.filter_by(medical_record_id=medicalRecordID).all()
    if not prescriptions:
        return jsonify({'error': 'Prescription not found for medical record'}), 404
    output = []
    for prescription in prescriptions:
        prescriptionData = {'prescriptionID': prescription.prescription_id
                        ,'medicalRecordID': prescription.medical_record_id
                        ,'medicineName': prescription.medicine_name
                        ,'dose': prescription.dose
                        }
        output.append(prescriptionData)
    return jsonify({'prescriptions': output})

@app.route("/prescription", methods=["POST"])
def addPrescription():
    data = request.json
    medicalRecordID = data.get('medicalRecordID')
    medicalRecord = MedicalRecord.query.filter_by(medical_record_id=medicalRecordID).first()
    if not medicalRecord:
        return jsonify({'error': 'medicalRecordID does not exist'}), 400
    newPrescription = Prescription(
        medical_record_id=data['medicalRecordID'],
        medicine_name=data['medicineName'],
        dose=data['dose']
    )
    newPrescription.inserted_timestamp = datetime.now()+ timedelta(hours=7)
    db.session.add(newPrescription)
    db.session.commit()
    return jsonify({'message': 'Prescription added successfully'}), 201

@app.route("/prescription/<int:prescriptionID>", methods=["PUT"])
def updatePrescription(prescriptionID):
    data = request.json
    medicalRecordID = data.get('medicalRecordID')
    prescription = Prescription.query.get(prescriptionID)
    if not prescription:
        return jsonify({'error': 'Prescription not found'}), 404
    medicalRecord = MedicalRecord.query.filter_by(medical_record_id=medicalRecordID).first()
    if not medicalRecord:
        return jsonify({'error': 'medicalRecordID does not exist'}), 400
    prescription.medical_record_id = data.get('medicalRecordID', prescription.medical_record_id)
    prescription.medicine_name = data.get('medicineName', prescription.medicine_name)
    prescription.dose = data.get('dose', prescription.dose)
    prescription.updated_timestamp = datetime.now()+ timedelta(hours=7)
    db.session.commit()
    return jsonify({'message': 'Prescription updated successfully'})

@app.route("/prescription/<int:prescriptionID>", methods=["DELETE"])
def deletePrescription(prescriptionID):
    prescription = Prescription.query.get(prescriptionID)
    if not prescription:
        return jsonify({'error': 'Prescription not found'}), 404
    db.session.delete(prescription)
    db.session.commit()
    return jsonify({'message': 'Prescription deleted successfully'})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)