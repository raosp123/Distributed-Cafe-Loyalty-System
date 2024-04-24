import psycopg2

# Function to get database connection
REPLICA_STATUS = True

def check_replica_promoted():
    global REPLICA_STATUS 
    try:
        conn = psycopg2.connect(
            dbname="postgres",
            user="postgres",
            password="enter1234",
            host="localhost",
            port="5433"
        )
        # print("Connected to the database")
    except psycopg2.Error as e:
        # print("Unable to connect to the database, Read-only replica has not been created yet:", e)
        exit()
    cur = conn.cursor()
    cur.execute("SELECT pg_is_in_recovery()")
    replica_status = cur.fetchone()[0]
    if replica_status == False:
        print("Replica is promoted")
        REPLICA_STATUS = False
    else:
        print("Replica is not promoted")
        REPLICA_STATUS = True 
    conn.close()
    return not replica_status

def get_db_connection(db_type="write"):
    print("Replica status",REPLICA_STATUS)
    #if we want to access the read replica
    if db_type=="read" or REPLICA_STATUS==False:
        try:
            conn = psycopg2.connect(
                dbname="postgres",
                user="postgres",
                password="enter1234",
                host="localhost",
                port="5433"
            )
            print("Connected to the database")
        except psycopg2.Error as e:
            print("Unable to connect to the database, Read-only replica has not been created yet:", e)
            exit()
        cur = conn.cursor()
    #access the master DB
    else:
        try:
            conn = psycopg2.connect(
                dbname="postgres",
                user="postgres",
                password="enter1234",
                host="localhost",
                port="5432"
            )
            print("Connected to the database")
        except psycopg2.Error as e:
            print("Unable to connect to the database:", e)
            if check_replica_promoted():
                conn = psycopg2.connect(
                    dbname="postgres",
                    user="postgres",
                    password="enter1234",
                    host="localhost",
                    port="5433"
                )
                print("Connected to the promoted database")
            else:
                exit()
        cur = conn.cursor()
        print("write")

    return conn, cur        

def create_user(user_id, loyalty_card_id, hashed_password):
    conn, cur = get_db_connection()
    try:
        print(f"Attempting to create user with ID: {user_id}, Loyalty Card ID: {loyalty_card_id}, Hashed Password: {hashed_password}")
        cur.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
        existing_user = cur.fetchone()
        if existing_user:
            raise ValueError("User with user ID {} already exists".format(user_id))

        cur.execute("SELECT * FROM loyalty_card WHERE loyalty_card_id = %s FOR UPDATE", (loyalty_card_id,))
        existing_card = cur.fetchone()

        if existing_card:
            num_users = existing_card[2]
            print(f"User {user_id}: Loyalty card {loyalty_card_id} exists with {num_users} amount of user")
            if num_users < 4:
                cur.execute("UPDATE loyalty_card SET num_users = num_users + 1 WHERE loyalty_card_id = %s", (loyalty_card_id,))
                print(f"User {user_id}: added to loyalty card.")
                cur.execute("INSERT INTO users (user_id, loyalty_card_id, hashed_password) VALUES (%s, %s, %s)", (user_id, loyalty_card_id, hashed_password))
                conn.commit()
                msg = (f"User {user_id} created successfully")
                return msg
            else:
                raise ValueError("Maximum number of users reached for loyalty card {}".format(loyalty_card_id))
        else:
            cur.execute("INSERT INTO loyalty_card (loyalty_card_id, num_transactions, num_users) VALUES (%s, 0, 1)", (loyalty_card_id,))
            cur.execute("INSERT INTO users (user_id, loyalty_card_id, hashed_password) VALUES (%s, %s, %s)", (user_id, loyalty_card_id, hashed_password))
            conn.commit()
            msg = (f"User {user_id} created successfully")
            return msg
    except psycopg2.Error as e:
        conn.rollback()
        msg = f"Error creating user {user_id}::", e
        return msg

def add_user_to_loyalty_group(user_id, loyalty_card_id):
    conn, cur = get_db_connection()
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
        print("Error adding user to loyalty group:", e)

def delete_user(user_id):
    conn, cur = get_db_connection()
    try:
        cur.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
        user_details = cur.fetchone()
        if user_details:
            print("here")
            loyalty_card_id = user_details[1]
            print("loyalty card id: ", loyalty_card_id)
            cur.execute("SELECT * FROM loyalty_card WHERE loyalty_card_id = %s", (loyalty_card_id,))
            existing_card = cur.fetchone()

            if existing_card:
                num_users = existing_card[2]
                print("num users: ", num_users)
                if num_users <=1:
                    cur.execute("DELETE FROM coupon WHERE loyalty_card_id = %s", (loyalty_card_id,))
                    cur.execute("DELETE FROM loyalty_card WHERE loyalty_card_id = %s", (loyalty_card_id,))
                else:
                    cur.execute("UPDATE loyalty_card SET num_users = num_users - 1 WHERE loyalty_card_id = %s", (loyalty_card_id,))

            cur.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
            conn.commit()
            print("User deleted successfully")
        else:
            raise ValueError("User with user ID {} does not exist".format(user_id))
    except psycopg2.Error as e:
        conn.rollback()
        print("Error deleting user:", e)

def make_transaction(user_id, coupon_value=None):
    conn, cur = get_db_connection()
    try:
        cur.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
        user_details = cur.fetchone()
        if user_details:
            loyalty_card_id = user_details[1]
            print("loyalty_card_id", loyalty_card_id)

            if coupon_value is not None:
                print("coupon value", coupon_value)
                cur.execute("DELETE FROM coupon WHERE ctid IN (SELECT ctid FROM coupon WHERE loyalty_card_id = %s AND coupon_value = %s FOR UPDATE SKIP LOCKED LIMIT 1 ) RETURNING 1", (loyalty_card_id, coupon_value))
                try:
                    deleted_rows = cur.fetchone()[0]
                except TypeError as e:
                    deleted_rows = 0
                if deleted_rows == 1:
                    print("Coupon successfully used")
                else:
                    raise ValueError(f"No available coupon of value {coupon_value} found for loyalty card {loyalty_card_id}")

            cur.execute("UPDATE loyalty_card SET num_transactions = num_transactions + 1 WHERE loyalty_card_id = %s", (loyalty_card_id,))
            cur.execute("SELECT num_transactions FROM loyalty_card WHERE loyalty_card_id = %s", (loyalty_card_id,))
            updated_num_transactions = cur.fetchone()[0]
            print("Updated num_transactions for loyalty_card_id {}: {}".format(loyalty_card_id, updated_num_transactions))
            
            give_coupon(loyalty_card_id, conn, cur)
            msg = (f"User {user_id}: Transaction added successfully")
            conn.commit()
            return msg
        else:
            raise ValueError("User with user ID {} does not exist".format(user_id))
            msg = (f"User {user_id}: Transaction failed")
            return msg
    except psycopg2.Error as e:
        conn.rollback()
        print("Error making transaction:", e)
        return e

def give_coupon(loyalty_card_id, conn, cur):
    print("give coupon")
    try:
        cur.execute("SELECT num_transactions FROM loyalty_card WHERE loyalty_card_id = %s", (loyalty_card_id,))
        num_transactions = cur.fetchone()[0] 
        print("num_transactions: ", num_transactions)
        if(num_transactions % 7 == 0):
            cur.execute("INSERT INTO coupon (coupon_value, loyalty_card_id) VALUES (%s, %s)", (20, loyalty_card_id))
            print("High coupon received")
        elif (num_transactions % 4 == 0):
            cur.execute("INSERT INTO coupon (coupon_value, loyalty_card_id) VALUES (%s, %s)", (10, loyalty_card_id))
            print("Low coupon received")
    except psycopg2.Error as e:
        conn.rollback()
        print("Error giving coupon:", e)

def list_users():
    conn, cur = get_db_connection("read")
    try:
        cur.execute("SELECT * FROM users")
        rows = cur.fetchall()
        return rows
    except psycopg2.Error as e:
        print("Error executing SQL query:", e)

def get_coupons(loyalty_card_id):
    conn, cur = get_db_connection("read")
    try:
        cur.execute("SELECT COUNT(*) FROM users WHERE loyalty_card_id = %s", (loyalty_card_id,))
        loyalty_card_exists = cur.fetchone()[0]

        if loyalty_card_exists:
            cur.execute("SELECT * FROM coupon WHERE loyalty_card_id = %s", (loyalty_card_id,))
            coupons = cur.fetchall()
            return coupons
        else:
            raise ValueError("Loyalty card {} does not exist".format(loyalty_card_id))
    except psycopg2.Error as e:
        print("Error fetching coupons:", e)
        return None

import threading

def test_select_lock_select():
    def run_query(thread_id):
        conn, cur = get_db_connection() 
        try:
            cur.execute("BEGIN")
            cur.execute("SELECT * FROM coupon WHERE loyalty_card_id = %s AND coupon_value = %s FOR UPDATE SKIP LOCKED LIMIT 1", (456, 20))
            selected_coupon = cur.fetchone()
            print(f"Thread {thread_id}: Selected coupon: {selected_coupon}")
            cur.execute("COMMIT")
        except Exception as e:
            print(f"Thread {thread_id}: Error: {e}")
            cur.execute("ROLLBACK") 
        finally:
            conn.close() 

    num_threads = 4

    threads = []
    for i in range(num_threads):
        thread = threading.Thread(target=run_query, args=(i,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

# Run the test
# test_select_lock_select()


def test_select_lock_delete():
    def run_query(thread_id):
        conn, cur = get_db_connection()
        try:
            cur.execute("BEGIN")
            cur.execute("DELETE FROM coupon WHERE ctid = (SELECT ctid FROM coupon WHERE loyalty_card_id = %s AND coupon_value = %s FOR UPDATE SKIP LOCKED LIMIT 1) RETURNING *", (456, 20))
            deleted_row = cur.fetchone()
            print(f"Thread {thread_id}: Deleted row: {deleted_row}")
            cur.execute("COMMIT")
        except Exception as e:
            print(f"Thread {thread_id}: Error: {e}")
            cur.execute("ROLLBACK") 
        finally:
            conn.close()  
    num_threads = 4

    threads = []
    for i in range(num_threads):
        thread = threading.Thread(target=run_query, args=(i,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

# Run the test
#test_select_lock_delete()

def simulate_concurrent_transactions():
    num_threads = 2
    users = [123, 1234]
    threads = []

    for i in range(num_threads):
        thread = threading.Thread(target=make_transaction, args=(users[i], 20)) 
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

# Run the simulation
# simulate_concurrent_transactions()

def simulate_concurrent_user_creation():
    num_threads = 3
    users = [(12345, 456, 'password1'), (123456, 456, 'password2'), (1234567, 456, 'password2')]
    threads = []

    for i in range(num_threads):
        user_id, loyalty_card_id, hashed_password = users[i]
        thread = threading.Thread(target=create_user, args=(user_id, loyalty_card_id, hashed_password))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

# Run the simulation
# simulate_concurrent_user_creation()