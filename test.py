import psycopg2
conn = psycopg2.connect(
    dbname="stripe_shop_db",
    user="postgres",
    password="Akanksha62@", 
    host="127.0.0.1",
    port="5432"
)
print("connected ok")
conn.close()