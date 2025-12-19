import sqlite3

def check_db():
    conn = sqlite3.connect("doctors.db")
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) FROM doctors WHERE is_active = 1")
    count = cur.fetchone()[0]
    print(f"Active doctors: {count}")
    
    cur.execute("SELECT specialization, COUNT(*) FROM doctors WHERE is_active = 1 GROUP BY specialization")
    specs = cur.fetchall()
    print("\nSpecialization Distribution:")
    for spec, count in specs:
        print(f"{spec}: {count}")
    
    conn.close()

if __name__ == "__main__":
    check_db()
