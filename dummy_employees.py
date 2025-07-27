from faker import Faker
import pandas as pd
import random
from google.cloud import storage
import io # To handle file-like objects in memory

# --- Configuration for GCS ---
GCS_BUCKET_NAME = "bkpemp-data" # <--- IMPORTANT: Replace with your actual GCS bucket name


def generate_dummy_employees(num_employees=100):
    
    fake = Faker('en_IN') # Using 'en_IN' locale for Indian names, addresses, etc.
    employees = []

    for _ in range(num_employees):
        gender = random.choice(['Male', 'Female', 'Other'])
        first_name = fake.first_name_male() if gender == 'Male' else fake.first_name_female() if gender == 'Female' else fake.first_name()
        last_name = fake.last_name()
        email = f"{first_name.lower()}.{last_name.lower()}@{fake.domain_name()}"
        
        employee = {
            "Employee ID": fake.unique.random_number(digits=5),
            "First Name": first_name,
            "Last Name": last_name,
            "Date of Birth": fake.date_of_birth(minimum_age=18, maximum_age=65).strftime("%Y-%m-%d"),
            "Gender": gender,
            "Email": email,
            "Phone Number": fake.phone_number(),
            "Address": fake.address(),
            "City": fake.city(),
            "State": fake.state(),
            "Zip Code": fake.postcode(),
            "SSN/National ID": fake.ssn(),
            "Bank Account Number": fake.bban(),
            "IFSC Code": fake.swift(),
            "Date of Hire": fake.date_between(start_date="-10y", end_date="today").strftime("%Y-%m-%d"),
            "Job Title": fake.job(),
            "Department": fake.word(ext_word_list=['HR', 'Engineering', 'Marketing', 'Sales', 'Finance', 'Operations']),
            "Salary": round(random.uniform(30000, 150000), 2),
            "Emergency Contact Name": fake.name(),
            "Emergency Contact Phone": fake.phone_number()
        }
        employees.append(employee)
    return employees

def save_to_csv_and_upload_to_gcs(data, local_filename="dummy_employees.csv", gcs_blob_name=""):
    
    df = pd.DataFrame(data)
    
    # Save to a BytesIO object (in-memory file)
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0) # Rewind the buffer to the beginning

    # Determine the GCS blob path
    if not gcs_blob_name:
        gcs_blob_name = local_filename
    
    

    try:
        # Initialize GCS client
        storage_client = storage.Client()
        bucket = storage_client.bucket(GCS_BUCKET_NAME)
        blob = bucket.blob(gcs_blob_name)

        # Upload the CSV data from the in-memory buffer
        blob.upload_from_string(csv_buffer.getvalue(), content_type="text/csv")
        print(f"Successfully uploaded {len(data)} dummy employees to gs://{GCS_BUCKET_NAME}/{gcs_blob_name}")

        # Optionally, save a local copy as well
        df.to_csv(local_filename, index=False)
        print(f"Successfully saved {len(data)} dummy employees to local file {local_filename}")

    except Exception as e:
        print(f"Error uploading to GCS: {e}")

if __name__ == "__main__":
    num_employees_to_generate = 5

    print(f"Generating {num_employees_to_generate} dummy employee records...")
    dummy_employee_data = generate_dummy_employees(num_employees_to_generate)

    # Define the local and GCS filenames
    local_csv_filename = "dummy_employees.csv"
    # Current timestamp for unique GCS filename, relevant for Pune IST
    import datetime
    pune_tz = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
    current_time_ist = datetime.datetime.now(pune_tz)
    gcs_csv_filename = f"dummy_employees_{current_time_ist.strftime('%Y%m%d_%H%M%S')}.csv"

    save_to_csv_and_upload_to_gcs(dummy_employee_data, local_filename=local_csv_filename, gcs_blob_name=gcs_csv_filename)

    # Optionally, print the first few records to verify
    print("\nFirst 5 dummy employee records (from generated data):")
    for i, emp in enumerate(dummy_employee_data[:5]):
        print(f"\nEmployee {i+1}:")
        for key, value in emp.items():
            print(f"  {key}: {value}")