#Can be used to re-arrange patients based on a key in the database
psql -U remote_care -d release2 -c "cluster patient_patient USING patient_patient_pkey"
