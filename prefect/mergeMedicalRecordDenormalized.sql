merge into analytic.medical_record_denormalized
using
       (
       select 
       pt.patient_id
       ,pt.id_card_num
       ,pt.first_name
       ,pt.last_name
       ,pt.birth_date
       ,pt.phone_num
       ,m.medical_record_id
       ,m.hospital_name
       ,m.doctor_full_name
       ,m.diagnosis
       ,m.symtom
       ,m.treatment_start_date
       ,m.treatment_end_date
       ,p.prescription_id
       ,p.medicine_name
       ,p.dose
       from stg.stg_patient pt 
       left join stg.stg_medical_record m 
       on pt.patient_id = m.patient_id 
       left join stg.stg_prescription p 
       on m.medical_record_id = p.medical_record_id
       where m.patient_id is not null 
       ) as src
on medical_record_denormalized.patient_id = src.patient_id
       and medical_record_denormalized.medical_record_id = src.medical_record_id
       and coalesce(medical_record_denormalized.prescription_id,0) = coalesce(src.prescription_id,0)
when matched then 
       update set 
              id_card_num = src.id_card_num
              ,first_name = src.first_name
              ,last_name = src.last_name
              ,birth_date = src.birth_date
              ,phone_num = src.phone_num
              ,hospital_name = src.hospital_name
              ,doctor_full_name = src.doctor_full_name
              ,diagnosis = src.diagnosis
              ,symtom = src.symtom
              ,treatment_start_date = src.treatment_start_date
              ,treatment_end_date = src.treatment_end_date
              ,medicine_name = src.medicine_name
              ,dose = src.dose
              ,updated_timestamp = current_timestamp
when not matched then 
       insert (patient_id,id_card_num,first_name,last_name,birth_date,phone_num,medical_record_id,hospital_name,doctor_full_name,diagnosis,symtom,treatment_start_date,treatment_end_date,prescription_id,medicine_name,dose,inserted_timestamp) 
              values (src.patient_id,src.id_card_num,src.first_name,src.last_name,src.birth_date,src.phone_num,src.medical_record_id,src.hospital_name,src.doctor_full_name,src.diagnosis,src.symtom,src.treatment_start_date,src.treatment_end_date,src.prescription_id,src.medicine_name,src.dose,current_timestamp);

delete from analytic.medical_record_denormalized
using (
select count(*) as cnt ,patient_id, medical_record_id 
from analytic.medical_record_denormalized 
group by patient_id, medical_record_id 
having count(*) > 1
) src
where medical_record_denormalized.patient_id = src.patient_id
and medical_record_denormalized.medical_record_id = src.medical_record_id
and prescription_id is null;