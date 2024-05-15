#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "postgres" --dbname "postgres" <<-EOSQL
	CREATE SCHEMA medical_app;
	CREATE TABLE medical_app.patient
        (
        patient_id serial primary key
        ,id_card_num varchar(13)
        ,first_name varchar(50)
        ,last_name varchar(50)
        ,birth_date date
        ,phone_num varchar(10)
        ,inserted_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ,updated_timestamp TIMESTAMP
        );
    CREATE TABLE medical_app.medical_record
        (
        medical_record_id serial primary key
        ,patient_id int
        ,hospital_name varchar(50)
        ,doctor_full_name varchar(50)
        ,diagnosis varchar(255)
        ,symtom varchar(255)
        ,treatment_start_date date
        ,treatment_end_date date
        ,inserted_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ,updated_timestamp TIMESTAMP
        );
    CREATE TABLE medical_app.prescription
        (
        prescription_id serial primary key
        ,medical_record_id int
        ,medicine_name varchar(50)
        ,dose varchar(50)
        ,inserted_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ,updated_timestamp TIMESTAMP
        );
EOSQL