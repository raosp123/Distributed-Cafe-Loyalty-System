
import requests
import concurrent.futures
from typing import Dict
DOMAIN_URL = 'http://localhost:8000/'

def create_user(user: Dict[str, str]) -> Dict[str, str]:
    url=DOMAIN_URL+'create/user/'
    response = requests.post(url, json=user)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": response.text}




# Example of a POST request with JSON data
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



#creates users sequentially
for data in create_users:
    print(create_user(data))
# creates users concurrently with the same loyalty card id with only one spot left

test_concurrent_user_creation=[{'user_id': 4,
    'password': 'mnop',
    'loyalty_card_id': 1},
    {'user_id': 5,
    'password': 'qrst',
    'loyalty_card_id': 1}]

with concurrent.futures.ThreadPoolExecutor() as executor:
    # Use list comprehension to start the tasks and collect the Future objects
    futures = [executor.submit(create_user, user) for user in test_concurrent_user_creation]

    # Wait for all tasks to complete and get their results
    results = [future.result() for future in concurrent.futures.as_completed(futures)]

print(results)

# scenario 2 immediate_access_after_coupon_is created()

transactions_to_get_coupon=[{'user_id': 1,},{'user_id': 2,},{'user_id': 1,}{ 'user_id': 2,}]
def immediate_access_after_coupon_is_created():
    url=DOMAIN_URL+'transactions/'

    for transaction in transactions_to_get_coupon:
        response = requests.post(url, json=transaction)
        if response.status_code == 200:
            print(response.json())
        else:
            print({"error": response.text}) 
    #fetch coupons of user 3 to check if it is credited with new coupon
    response = requests.get(DOMAIN_URL+'coupons/1')
    print(response.json())

            
#use coupon of same value when only 1 coupons are available
    



    
# possible to create 5 users with same loyalty card id
    # Expected false
# scenario 1: get coupons of two users from same loyalty card
    # use same coupon value for both users
        #with only one coupon of that value?
    # use different coupon values for both users  

# scenario 2: get coupons of two users from different loyalty cards

#scenario 3: coupon should get credited to user's account after transaction at another location 
    