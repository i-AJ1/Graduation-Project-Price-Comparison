import os
import mysql.connector

def get_db():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", "YOUR_PASSWORD"),
        database=os.getenv("DB_NAME", "price_compare")
    )

def query(sql, params=None, fetchone=False, commit=False):
    db = get_db()
    cur = db.cursor(dictionary=True)
    try:
        if params:
            cur.execute(sql, params)
        else:
            cur.execute(sql)

        if commit:
            db.commit()
            return cur.lastrowid

        if fetchone:
            return cur.fetchone()

        return cur.fetchall()

    except Exception as e:
        print("DB ERROR:", e)
        db.rollback()
        raise

    finally:
        cur.close()
        db.close()