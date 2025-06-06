import psycopg2
from psycopg2 import Error
from dotenv import load_dotenv
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from psycopg2 import sql

load_dotenv()

def create_database(host, user, password, new_db_name):
    """
    Connect to PostgreSQL and create a new database
    
    Parameters:
    host (str): Database server host
    user (str): Username for PostgreSQL
    password (str): Password for PostgreSQL
    new_db_name (str): Name of the new database to create
    
    Returns:
    bool: True if successful, False if failed
    """
    
    try:
        connection = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            database="postgres"
        )
        connection.autocommit = True
        
        cursor = connection.cursor()
        
        sql_create_database = f"CREATE DATABASE {new_db_name};"
        
        cursor.execute(sql_create_database)
        print(f"Database '{new_db_name}' created successfully")
         
        connection.close()
        
        new_connection = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            database=new_db_name
        )
        print(f"Successfully connected to database '{new_db_name}'")
        new_connection.close()
        
        return True

    except (Exception, Error) as error:
        print("Error while connecting to PostgreSQL:", error)
        return False
        
    finally:
        if 'connection' in locals():
            if connection:
                cursor.close()
                connection.close()
                print("PostgreSQL connection closed")


def fill_the_database(host, new_db_name, port, user, password, sql_file_path = 'chinook_postgreSql_short.sql'):
    """
    Read SQL file and execute all commands at once
    
    Parameters:
    host (str): Database server host
    database (str): Database name
    user (str): Username for PostgreSQL
    password (str): Password for PostgreSQL
    sql_file_path (str): Path to the SQL file
    
    Returns:
    bool: True if successful, False if failed
    """

    sql_file_path = 'chinook_postgreSql_short.sql'
    connection = None
    cursor = None
    try:
        connection = psycopg2.connect(
            host=host,
            database=new_db_name,
            user=user,
            port=port,
            password=password
        )
        
        cursor = connection.cursor()
        
        with open(sql_file_path, 'r', encoding='utf-8') as sql_file:
            sql_commands = sql_file.read()
        
        cursor.execute(sql_commands)
        
        connection.commit()
        
        print("Database filled successfully!")
        return True
        
    except (Exception, Error) as error:
        print("Error while executing SQL commands:", error)
        if connection:
            connection.rollback()
        return False
        
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
            print("PostgreSQL connection closed")

def check_database_exists(dbname, host, port, user, password, new_dbname):
    try:
        conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
        conn.autocommit = True
        
        with conn.cursor() as cur:
            cur.execute("SELECT datname FROM pg_database WHERE datname = %s", (new_dbname,))
            exists = cur.fetchone() is not None
            
        conn.close()
        return exists
        
    except psycopg2.Error as e:
        print(f"Error checking database: {e}")
        return False


def check_create_db(dbname, host, port, user, password, new_dbname):
    if not check_database_exists(dbname, host, port, user, password, new_dbname):
        create_database(host, user, password, new_dbname)


def check_tables_exist(host, new_db_name, port, user, password):
    
    try:
        conn = psycopg2.connect(dbname=new_db_name, user=user, password=password, host=host, port=port)
        with conn.cursor() as cur:
            cur.execute(f"""
                        SELECT COUNT(*) 
                        FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_catalog = '{new_db_name}'
                        AND table_name IN ('Courts', 'Cases');
            """)
            count = cur.fetchone()[0]
        return count == 2
    except:
        return False   

def check_fill_db(host, new_db_name, port, user, password, sql_file_path):
    print('checking if tables exist')
    if not check_tables_exist(host, new_db_name, port, user, password):
        fill_the_database(host, new_db_name, port, user, password, sql_file_path)
        print('database was filled')
        return True

def create_readonly_user(host, database, user, password, new_user_name, agent_read_password):
    """
    Create a read-only user if it doesn't exist and grant necessary permissions
    """
    import psycopg2
    from psycopg2 import sql
    
    conn = psycopg2.connect(host=host, database=database, user=user, password=password)
    conn.autocommit = True
    cur = conn.cursor()

    try:
        cur.execute(
            "SELECT 1 FROM pg_roles WHERE rolname = %s",
            (new_user_name,)
        )
        user_exists = cur.fetchone() is not None

        if not user_exists:
            cur.execute(
                sql.SQL("CREATE USER {user} WITH PASSWORD %s;").format(
                    user=sql.Identifier(new_user_name)
                ),
                [agent_read_password]
            )

            cur.execute(
                sql.SQL("GRANT CONNECT ON DATABASE {db} TO {user};").format(
                    db=sql.Identifier(database),
                    user=sql.Identifier(new_user_name)
                )
            )

            cur.execute(
                sql.SQL("GRANT USAGE ON SCHEMA public TO {user};").format(
                    user=sql.Identifier(new_user_name)
                )
            )

            cur.execute(
                sql.SQL("GRANT SELECT ON ALL TABLES IN SCHEMA public TO {user};").format(
                    user=sql.Identifier(new_user_name)
                )
            )

            cur.execute(
                sql.SQL("ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO {user};").format(
                    user=sql.Identifier(new_user_name)
                )
            )

            print(f"Created read-only user '{new_user_name}' with all necessary permissions")
        else:
            print(f"User '{new_user_name}' already exists")

    except Exception as e:
        print(f"Error creating read-only user: {str(e)}")
        raise
    finally:
        cur.close()
        conn.close()

def database_exists(conn, db_name):
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", (db_name,))
        return cur.fetchone() is not None

def create_postgres_database(db_name, host, port, user, password):
    conn = psycopg2.connect(dbname="postgres", user=user, password=password, host=host, port=port)

    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()

    try:
        cursor.execute(sql.SQL("DROP DATABASE IF EXISTS {}").format(sql.Identifier(db_name)))
        print(f"Database {db_name} dropped successfully (if it existed).")
    except psycopg2.Error as e:
        print(f"An error occurred while dropping the database: {e}")
        cursor.close()
        conn.close()
        return

    try:
        cursor.execute(sql.SQL("CREATE DATABASE {}").format(
            sql.Identifier(db_name)))
        print(f"Database {db_name} created successfully.")
    except psycopg2.Error as e:
        print(f"An error occurred: {e}")
    finally:
        cursor.close()
        conn.close()

def execute_sql(connection, sql_script):
    cursor = connection.cursor()
    try:
        cursor.execute(sql_script)
        connection.commit()
        print("Query executed successfully")
    except psycopg2.Error as e:
        print(f"An error occurred: {e}")
    finally:
        cursor.close()

def run_sql_commands(db_name, host, port, user, password, sql_commands):
    conn = psycopg2.connect(dbname=db_name, user=user, password=password, host=host, port=port)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

    for n,command in enumerate(sql_commands):
        print(n)
        execute_sql(conn, command)

    conn.close()