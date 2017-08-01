


==test_users.json:==
python manage.py dumpdata account.user account.encryptionkey auth.group healthperson patient secretariat healthprofessional management lists.hospital  --indent=4 > test_users.json

When replaced check:
- management\test.py it contains hardcoded DOB for patient search and function/specialism for healthprofessional
- make sure the questionnaire.ibdnauseavomittime instance are included
- Check content types on polymorhpic types