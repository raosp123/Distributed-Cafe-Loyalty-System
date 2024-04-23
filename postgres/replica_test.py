import subprocess
import time

DOMAIN_URL = 'http://localhost:8000/'

def delete_docker_compose_service(service_name):
    try:
        subprocess.check_call(['docker-compose', 'rm', '-f', '-s', '-v', service_name])
        print(f'Successfully removed service: {service_name}')
    except subprocess.CalledProcessError as e:
        print(f'Failed to remove service: {service_name}. Error: {e.output}')

# Call the function with the service name
delete_docker_compose_service('postgres-db-primary')

time.sleep(120)

import requests

def create_user(user):
    url=DOMAIN_URL+'create/user/'
    response = requests.post(url, json=user)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": response.text}
    
data= [{'user_id': 10,
    'password': 'abcd',
    'loyalty_card_id': 4},]

print(create_user(data))