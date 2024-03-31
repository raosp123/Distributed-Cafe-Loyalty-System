import psycopg2

# Function to get database connection
def get_db_connection(db_type="write"):

    #if we want to access the read replica
    if db_type=="read":
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
            exit()
        cur = conn.cursor()
        print("write")

    return conn, cur

def create_user(user_id, loyalty_card_id, hashed_password):
    conn, cur = get_db_connection()
    try:
        cur.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
        existing_user = cur.fetchone()
        if existing_user:
            raise ValueError("User with user ID {} already exists".format(user_id))

        cur.execute("SELECT * FROM loyalty_card WHERE loyalty_card_id = %s", (loyalty_card_id,))
        existing_card = cur.fetchone()

        if existing_card:
            num_users = existing_card[2]
            if num_users < 4:
                cur.execute("UPDATE loyalty_card SET num_users = num_users + 1 WHERE loyalty_card_id = %s", (loyalty_card_id,))
            else:
                raise ValueError("Maximum number of users reached for loyalty card {}".format(loyalty_card_id))
        else:
            cur.execute("INSERT INTO loyalty_card (loyalty_card_id, num_transactions, num_users) VALUES (%s, 0, 1)", (loyalty_card_id,))

        cur.execute("INSERT INTO users (user_id, loyalty_card_id, hashed_password) VALUES (%s, %s, %s)", (user_id, loyalty_card_id, hashed_password))
        conn.commit()
        print("User created successfully")
    except psycopg2.Error as e:
        conn.rollback()
        print("Error creating user:", e)

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

            print(existing_card)

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

def make_transaction(user_id):
    conn, cur = get_db_connection()
    try:
        cur.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
        user_details = cur.fetchone()
        if user_details:
            loyalty_card_id = user_details[1]
            cur.execute("UPDATE loyalty_card SET num_transactions = num_transactions + 1 WHERE loyalty_card_id = %s", (loyalty_card_id,))
            cur.execute("SELECT num_transactions FROM loyalty_card WHERE loyalty_card_id = %s", (loyalty_card_id,))
            updated_num_transactions = cur.fetchone()[0]
            print("Updated num_transactions for loyalty_card_id {}: {}".format(loyalty_card_id, updated_num_transactions))
            
            give_coupon(loyalty_card_id, conn, cur)
            print("Transaction added successfully")
        else:
            raise ValueError("User with user ID {} does not exist".format(user_id))
            print("Transaction failed")
        conn.commit()
    except psycopg2.Error as e:
        conn.rollback()
        print("Error making transaction:", e)

def give_coupon(loyalty_card_id, conn, cur):
    try:
        cur.execute("SELECT num_transactions FROM loyalty_card WHERE loyalty_card_id = %s", (loyalty_card_id,))
        num_transactions = cur.fetchone()[0] 
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
    conn, cur = get_db_connection()
    try:
        cur.execute("SELECT * FROM users")
        rows = cur.fetchall()
        return rows
    except psycopg2.Error as e:
        print("Error executing SQL query:", e)

def get_coupons(loyalty_card_id):
    conn, cur = get_db_connection()
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

def use_coupon(loyalty_card_id, coupon_value):
    conn, cur = get_db_connection()
    try:
        cur.execute("SELECT COUNT(*) FROM users WHERE loyalty_card_id = %s", (loyalty_card_id,))
        loyalty_card_exists = cur.fetchone()[0]

        if loyalty_card_exists:
            cur.execute("SELECT COUNT(*) FROM coupon WHERE loyalty_card_id = %s AND coupon_value = %s", (loyalty_card_id, coupon_value))
            coupon_exists = cur.fetchone()[0]

            if coupon_exists:
                cur.execute("DELETE FROM coupon WHERE loyalty_card_id = %s AND coupon_value = %s", (loyalty_card_id, coupon_value))
                conn.commit()
                print("Coupon successfully used")
            else:
                raise ValueError(f"No coupon of value {coupon_value} found for loyalty card {loyalty_card_id}")
        else:
            raise ValueError("Loyalty card {} does not exist".format(loyalty_card_id))

    except psycopg2.Error as e:
        conn.rollback()
        print("Error using coupon:", e)
        return {"message": "Error using coupon. Please try again later."}