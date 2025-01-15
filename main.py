# Импортируем необходимые библиотеки
import psycopg2
from faker import Faker
import random
from datetime import datetime, timedelta

# Создаем экземпляр Faker для генерации фейковых данных
fake = Faker()

# Подключаемся к базе данных PostgreSQL
conn = psycopg2.connect(
    dbname="Your_DB_Name",  # Название базы данных
    user="Username",        # Имя пользователя
    password="Password",    # Пароль
    host="127.0.0.1",      # Хост
    port="5432"             # Порт
)
cur = conn.cursor()

# Генерация данных для таблицы "Пациенты"
num_patients = 5000  # Количество пациентов
patient_ids = []  # Список для хранения идентификаторов пациентов
for _ in range(num_patients):
    cur.execute("""
        INSERT INTO patients (first_name, last_name, date_of_birth, gender, address, phone, email)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING patient_id
    """, (
        fake.first_name(),  # Имя
        fake.last_name(),   # Фамилия
        fake.date_of_birth(minimum_age=18, maximum_age=90),  # Дата рождения
        random.choice(['Male', 'Female']),  # Пол
        fake.address(),     # Адрес
        fake.phone_number()[:20],  # Ограничиваем длину до 20 символов
        fake.email()        # Электронная почта
    ))
    patient_id = cur.fetchone()[0]  # Получаем идентификатор пациента
    patient_ids.append(patient_id)  # Добавляем идентификатор в список

# Генерация данных для таблицы "Врачи"
num_doctors = 100  # Количество врачей
doctor_ids = []  # Список для хранения идентификаторов врачей
for _ in range(num_doctors):
    cur.execute("""
        INSERT INTO doctors (first_name, last_name, specialization, phone, email)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING doctor_id
    """, (
        fake.first_name(),  # Имя
        fake.last_name(),   # Фамилия
        fake.job(),         # Специализация
        fake.phone_number()[:20],  # Ограничиваем длину до 20 символов
        fake.email()        # Электронная почта
    ))
    doctor_id = cur.fetchone()[0]  # Получаем идентификатор врача
    doctor_ids.append(doctor_id)  # Добавляем идентификатор в список

# Генерация данных для таблицы "Медицинские_записи"
num_records = 10000  # Количество медицинских записей
for _ in range(num_records):
    patient_id = random.choice(patient_ids)  # Случайный пациент
    doctor_id = random.choice(doctor_ids)    # Случайный врач
    cur.execute("""
        INSERT INTO medical_records (patient_id, doctor_id, appointment_date, symptoms, diagnosis, prescribed_treatment, test_results)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (
        patient_id,  # Идентификатор пациента
        doctor_id,   # Идентификатор врача
        fake.date_between(start_date='-1y', end_date='today'),  # Дата приема
        fake.text(max_nb_chars=100),  # Симптомы
        fake.text(max_nb_chars=100),  # Диагноз
        fake.text(max_nb_chars=100),  # Назначенное лечение
        fake.text(max_nb_chars=100)    # Результаты тестов
    ))

# Генерация данных для таблицы "Расписание_приема"
num_schedules = 5000  # Количество расписаний
for _ in range(num_schedules):
    doctor_id = random.choice(doctor_ids)  # Случайный врач
    patient_id = random.choice(patient_ids)  # Случайный пациент
    cur.execute("""
        INSERT INTO appointment_schedule (doctor_id, appointment_datetime, patient_id)
        VALUES (%s, %s, %s)
    """, (
        doctor_id,  # Идентификатор врача
        fake.date_time_between(start_date='-1y', end_date='+1y'),  # Дата и время приема
        patient_id  # Идентификатор пациента
    ))

# Генерация данных для таблицы "Страховые_полисы"
num_policies = 5000  # Количество страховых полисов
used_patient_ids = set()  # Множество для отслеживания использованных идентификаторов пациентов
for _ in range(num_policies):
    patient_id = random.choice(patient_ids)  # Случайный пациент
    while patient_id in used_patient_ids:  # Проверяем, использовался ли пациент ранее
        patient_id = random.choice(patient_ids)  # Если да, выбираем другого
    used_patient_ids.add(patient_id)  # Добавляем идентификатор в множество
    cur.execute("""
        INSERT INTO insurance_policies (policy_number, issue_date, expiration_date, patient_id)
        VALUES (%s, %s, %s, %s)
    """, (
        fake.uuid4(),  # Номер полиса
        fake.date_between(start_date='-5y', end_date='-1y'),  # Дата выдачи
        fake.date_between(start_date='+1y', end_date='+5y'),  # Дата окончания
        patient_id  # Идентификатор пациента
    ))

# Сохраняем изменения и закрываем соединение с базой данных
conn.commit()  # Подтверждаем изменения
cur.close()    # Закрываем курсор
conn.close()   # Закрываем соединение с базой данных
