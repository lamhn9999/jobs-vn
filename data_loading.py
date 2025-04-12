import mysql.connector
import pandas as pd

jobdb = mysql.connector.connect(
  host="",
  port = ,
  user="",
  password="",
  database = "job_desc_db"
)
my_cursor = jobdb.cursor()

def reset_auto_increment(table_name):
    my_cursor.execute(f"SELECT MAX({table_name + '_id'}) FROM {table_name}")
    max_id = my_cursor.fetchone()[0] or 0
    next_id = max_id + 1
    my_cursor.execute(f"ALTER TABLE {table_name} AUTO_INCREMENT = {next_id}")
    jobdb.commit()

def concat(row_idx):
  global df_no_cl
  return pd.Series(df_no_cl.iloc[int(row_idx)][['description', 'job_id', 'min_salary', 'max_salary', 'currency', 'created_at', 'expired_at']], index = ['description', 'job_id', 'min_salary', 'max_salary', 'currency', 'created_at', 'expired_at'])

df_no_cl = pd.DataFrame()
df_no_cl[['description', 'job_id']] = pd.read_csv('transformed_job_desc.csv', usecols = ['job_desc', 'job_id'])
df_no_cl[['min_salary', 'max_salary', 'currency']] = pd.read_csv('transformed_salary.csv')
df_no_cl[['created_at', 'expired_at']] = pd.read_csv('transformed_time.csv')

df = pd.read_csv('transformed_company_location.csv', usecols = ['index', 'company_id'])
df[['description', 'job_id', 'min_salary', 'max_salary', 'currency', 'created_at', 'expired_at']] = df['index'].apply(concat)
df[['company_id', 'description', 'job_id', 'min_salary', 'max_salary', 'currency', 'created_at', 'expired_at']].to_csv('data_fully_transformed.csv', index = False)

def safe_int(x):
    if pd.notnull(x):
        return int(x)
    else:
      return None

reset_auto_increment("job_desc")
for row in df.itertuples():
    insert_command = """
        INSERT INTO job_desc(
            company_id, description, job_id, min_salary, max_salary, currency,
            created_at, expired_at, isactive
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    created_at = pd.to_datetime(row.created_at)
    expired_at = created_at + pd.Timedelta(days = int(row.expired_at))
    
    values = (
        safe_int(row.company_id),
        row.description,
        safe_int(row.job_id),
        safe_int(row.min_salary),
        safe_int(row.max_salary),
        row.currency,
        created_at,
        expired_at,
        True
    )

    my_cursor.execute(insert_command, values)
    jobdb.commit()

my_cursor.execute("UPDATE job_desc SET isactive = IF(CURRENT_TIMESTAMP < expired_at, 1, 0);")
jobdb.commit()

jobdb.close()


