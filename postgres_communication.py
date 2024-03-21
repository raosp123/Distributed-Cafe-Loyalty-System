import psycopg2

try:
    conn = psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="enter1234",
        host="localhost"
    )
    print("Connected to the database")
except psycopg2.Error as e:
    print("Unable to connect to the database:", e)
    exit()

cur = conn.cursor()

def create_user(user_id, loyalty_card_id):
    try:
        cur.execute("SELECT * FROM loyalty_card WHERE loyalty_card_id = %s", (loyalty_card_id,))
        existing_card = cur.fetchone()

        if existing_card:
            num_users = existing_card[2]
            if num_users < 4:
                cur.execute("UPDATE loyalty_card SET num_users = num_users + 1 WHERE loyalty_card_id = %s", (loyalty_card_id,))
            else:
                print("Maximum number of users reached for loyalty card {}".format(loyalty_card_id))
                return
        else:
            cur.execute("INSERT INTO loyalty_card (loyalty_card_id, num_transactions, num_users) VALUES (%s, 0, 1)", (loyalty_card_id,))

        cur.execute("INSERT INTO users (user_id, loyalty_card_id) VALUES (%s, %s)", (user_id, loyalty_card_id))
        conn.commit()
        print("User created successfully")
    except psycopg2.Error as e:
        conn.rollback()
        print("Error creating user:", e)

def add_user_to_loyalty_group(user_id, loyalty_card_id):
    try:
        cur.execute("SELECT * FROM loyalty_card WHERE loyalty_card_id = %s", (loyalty_card_id,))
        existing_card = cur.fetchone()

        if existing_card:
            num_users = existing_card[2]
            if num_users < 4:
                cur.execute("UPDATE loyalty_card SET num_users = num_users + 1 WHERE loyalty_card_id = %s", (loyalty_card_id,))
            else:
                print("Maximum number of users reached for loyalty card {}".format(loyalty_card_id))
                return
        cur.execute("UPDATE users SET loyalty_card_id = %s WHERE user_id = %s", (loyalty_card_id, user_id))
        conn.commit()
        print("User updated successfully")
    except psycopg2.Error as e:
        conn.rollback()
        print("Error creating user:", e)

def delete_user(user_id):
    try:
        cur.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
        user_details = cur.fetchone()
        if user_details:
            loyalty_card_id = user_details[1]

            cur.execute("SELECT * FROM loyalty_card WHERE loyalty_card_id = %s", (loyalty_card_id,))
            existing_card = cur.fetchone()

            if existing_card:
                num_users = existing_card[2]
                if num_users <=1:
                    cur.execute("DELETE FROM loyalty_card WHERE loyalty_card_id = %s", (loyalty_card_id,))
                else:
                    cur.execute("UPDATE loyalty_card SET num_users = num_users - 1 WHERE loyalty_card_id = %s", (loyalty_card_id,))

            cur.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
            conn.commit()
            print("User deleted successfully")
        else:
            print("User with user ID {} does not exist".format(user_id))
    except psycopg2.Error as e:
        conn.rollback()
        print("Error deleting user:", e)

def make_transaction(user_id):
    try:
        cur.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
        user_details = cur.fetchone()
        if user_details:
            loyalty_card_id = user_details[1]
            cur.execute("UPDATE loyalty_card SET num_transactions = num_transactions + 1 WHERE loyalty_card_id = %s", (loyalty_card_id,))
            cur.execute("SELECT num_transactions FROM loyalty_card WHERE loyalty_card_id = %s", (loyalty_card_id,))
            print("Num {} ".format(cur.fetchone()))
            give_coupon(loyalty_card_id)
        else:
            print("User with user ID {} does not exist".format(user_id))
        conn.commit()
        print("Transaction added successfully")
    except psycopg2.Error as e:
        conn.rollback()
        print("Error deleting user:", e)

def give_coupon(loyalty_card_id):
    try:
        cur.execute("SELECT * FROM loyalty_card WHERE loyalty_card_id = %s", (loyalty_card_id,))
        existing_card = cur.fetchone()
        num_transactions = existing_card[1]
        if(num_transactions % 7 == 0):
            cur.execute("INSERT INTO coupon_card_relation (loyalty_card_id, coupon_id) VALUES (%s, %s)", (loyalty_card_id, 2))
            print("High coupon received")
        elif (num_transactions % 4 == 0):
            cur.execute("INSERT INTO coupon_card_relation (loyalty_card_id, coupon_id) VALUES (%s, %s)", (loyalty_card_id, 1))
            print("Low coupon received")
    except psycopg2.Error as e:
        conn.rollback()
        print("Error deleting user:", e)


def list_users():
    try:
        cur.execute("SELECT * FROM users")
    
        rows = cur.fetchall()
        for row in rows:
            print(row)
    except psycopg2.Error as e:
        print("Error executing SQL query:", e)


create_user(333,15)
list_users()
delete_user(333)
list_users()
make_transaction(111)

cur.close()
conn.close()
