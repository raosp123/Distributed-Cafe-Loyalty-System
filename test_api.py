
import requests
import concurrent.futures
from typing import Dict
DOMAIN_URL = 'http://localhost:80/'

def create_user(user: Dict[str, str]) -> Dict[str, str]:
    url=DOMAIN_URL+'create/user/'
    response = requests.post(url, json=user)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": response.text}




# # Example of a POST request with JSON data
create_users = [{'user_id': 1,
    'password': 'abcd',
    'loyalty_card_id': 1},
    {'user_id': 2,
     'password': 'efgh',
     'loyalty_card_id': 1},
    {'user_id': 3,
    'password': 'ijkl',
    'loyalty_card_id': 1},
    {'user_id': 6,
        'password': 'uvwx',
        'loyalty_card_id': 2},
    {'user_id': 7,
    'password': 'yzab',
    'loyalty_card_id': 2},
]



# #creates users sequentially
def create_users_sequentially():
    for data in create_users:
        print(create_user(data))
# # creates users concurrently with the same loyalty card id with only one spot left

test_concurrent_user_creation=[{'user_id': 4,
    'password': 'mnop',
    'loyalty_card_id': 1},
    {'user_id': 5,
    'password': 'qrst',
    'loyalty_card_id': 1}]

def create_users_concurrently():
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Use list comprehension to start the tasks and collect the Future objects
        futures = [executor.submit(create_user, user) for user in test_concurrent_user_creation]

        # Wait for all tasks to complete and get their results
        results = [future.result() for future in concurrent.futures.as_completed(futures)]

    print(results)

# scenario 2 immediate_access_after_coupon_is created()

transactions_to_get_coupon=[{'user_id': 1},{'user_id': 2},{'user_id': 1},{ 'user_id': 2}]
def immediate_access_after_coupon_is_created():
    print("making transactions  with user id 1 and 2 with loyalty card 1 to get coupons( 4 transactions gives 1 coupon of 10 off value)")
    for transaction in transactions_to_get_coupon:
        print(use_coupon_transaction(transaction))         
    #fetch coupons of user 3 to check if it is credited with new coupon
    response = requests.get(DOMAIN_URL+'coupons/1')
    print(response.json())

            
# immediate_access_after_coupon_is_created()
# #use coupon of same value when only 1 coupons are available
    

def use_coupon_transaction(transaction):
    url=DOMAIN_URL+'transactions/'
    try:
        response = requests.post(url, json=transaction, timeout=5)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": response.text}
    except requests.exceptions.Timeout:
        print("The request timed out")
        return None

def use_coupon_of_same_value():
    url=DOMAIN_URL+'transactions/'
    #fetch coupons of user 1 and 2 to check if it is credited with new coupon
    response_1 = requests.get(DOMAIN_URL+'coupons/1')
    print(response_1.json())
    response_2 = requests.get(DOMAIN_URL+'coupons/1')
    print(response_2.json())

    transactions=[{'user_id': 1, 'coupon_value': response_1.json()[0][1]},
    {'user_id': 2, 'coupon_value': response_2.json()[0][1]}]
    with concurrent.futures.ThreadPoolExecutor() as executor:
    # Use list comprehension to start the tasks and collect the Future objects
        futures = [executor.submit(use_coupon_transaction, transaction) for transaction in transactions]

        # Wait for all tasks to complete and get their results
        results = [future.result() for future in concurrent.futures.as_completed(futures)]

    print(results)

# use_coupon_of_same_value()
# possible to create 5 users with same loyalty card id
    # Expected false
# scenario 1: get coupons of two users from same loyalty card
    # use same coupon value for both users
        #with only one coupon of that value?
    # use different coupon values for both users  

# scenario 2: get coupons of two users from different loyalty cards

#scenario 3: coupon should get credited to user's account after transaction at another location 
if __name__ == '__main__':
    # print("Running first test concurrent_user_creation checking 5 members in loyalty group with 1 spot left")
    # print("First creating 4 users with loyalty card id 1 and then creating 2 users concurrently with loyalty card id 1")
    # create_users_sequentially()
    # # # creates users concurrently with the same loyalty card id with only one spot left
    # print("The result of this test one user should be creates successfully and the other should fail")
    # print("This shows consistency and that our database can handle concurrent requests and transactions and serially execute them to maintain consistency and integrity of the data")
    # create_users_concurrently()
    # print("Running second test  immediate_access_after_coupon_is_created")
    # immediate_access_after_coupon_is_created()
    # print("The expected result of the above test is an ouput like this [[7, 20, 1]] showing that the coupon that was generated by the transactions of other users can be accessed by any other user instantaenously through the replica database  ")
    # print("This demonstrates consistency between globally acessible databases  and coponns created in frnace can immediately be accessed in ireland etc.")
    print("Running third test use_coupon_of_same_value when only 1 coupons are available")
    use_coupon_of_same_value()
    print("The expected result of the above test is that two transactions are made with the same coupon value and the second transaction should fail because the coupon has already been used")
    print("This demonstrates that the coupon is only available for one use and that the database is consistent and can handle multiple requests and transactions")
    