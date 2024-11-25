import psycopg2
from psycopg2 import OperationalError
try:
    # Connect to the PostgreSQL database
    conn = psycopg2.connect(
        database="postgres",  # Replace with your database name
        user="postgres",      # Replace with your username
        password="Awesome123",  # Replace with your password
        host="database-1.cfssqcm06z8w.us-east-2.rds.amazonaws.com",
        port="5432"
    )

    # Create a cursor object
    cursor = conn.cursor()

    # SQL to create the users table
    create_table_query = """
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        age INT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    cursor.execute(create_table_query)
    print("Table 'users' created successfully.")

    # Insert 5 users into the table
    insert_users_query = """
    INSERT INTO users (name, email, age)
    VALUES 
        ('John Doe', 'john@example.com', 25),
        ('Jane Smith', 'jane@example.com', 30),
        ('Alice Johnson', 'alice@example.com', 22),
        ('Bob Brown', 'bob@example.com', 28),
        ('Charlie White', 'charlie@example.com', 35)
    RETURNING id;
    """
    cursor.execute(insert_users_query)
    inserted_ids = cursor.fetchall()
    print(f"Inserted users with IDs: {inserted_ids}")

    # Commit the transaction
    conn.commit()

except OperationalError as e:
    print("Error connecting to the database:", e)

finally:
    # Ensure the connection is closed
    if 'conn' in locals() and conn:
        conn.close()
        print("Database connection closed.")