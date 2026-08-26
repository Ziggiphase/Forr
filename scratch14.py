import psycopg
conn = psycopg.connect('postgresql://forr:forr_dev@localhost:5432/forr_db')
cur = conn.cursor()
cur.execute('SELECT conversation_id, sender_type, content FROM messages ORDER BY created_at ASC;')
for row in cur.fetchall():
    print(ascii(row))
