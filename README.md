# covid19
This project provides a Python-based tool to filter COVID-19 affected cases for Tamil Nadu by date and district.

### Database
```sql
CREATE DATABASE covid19;
CREATE USER covid19 WITH ENCRYPTED PASSWORD 'covid19';
ALTER DATABASE covid19 OWNER TO covid19;
GRANT ALL PRIVILEGES ON DATABASE covid19 TO covid19;
GRANT USAGE, CREATE ON SCHEMA public TO covid19;
ALTER DATABASE covid19 SET TIMEZONE TO 'Asia/Kolkata';
ALTER USER covid19 CREATEDB CREATEROLE LOGIN;
```
