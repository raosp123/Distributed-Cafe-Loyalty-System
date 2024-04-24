import subprocess
import time

DOMAIN_URL = 'http://localhost:80/'

def delete_docker_compose_service(service_name):
    try:
        subprocess.check_call(['docker-compose', 'rm', '-f', '-s', '-v', service_name])
        print(f'Successfully removed service: {service_name}')
    except subprocess.CalledProcessError as e:
        print(f'Failed to remove service: {service_name}. Error: {e.output}')

# Call the function with the service name
delete_docker_compose_service('api3')

time.sleep(10)

import requests

def create_user(user):
    url=DOMAIN_URL+'create/user/'
    response = requests.post(url, json=user)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": response.text}
    
data= {'user_id': 11,
    'password': 'abcd',
    'loyalty_card_id': 5}

print(create_user(data))