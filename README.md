# Distributed Coffee Loyalty System

## Windows Compatibility Issues

Sometimes you will get an error with the docker mounts that something isn't working.

Current solution is to open the script file that is not working correctly in VScode, then change the Line Ending format on the bottom right of your VScode windows from CRLF -> LF, then save the file. It should work afterwards


## Pipeline setup

1. setup fastAPI

2. setup Postgres

3. run `docker compose -f postgres/docker-compose.yaml up -d` to stat the postgres container

4. run `docker-compose -f load_balancer/docker-compose.yml up -d` to start the NGINX and 3 backend servers (on ports 8001, 8002, 8003)

5. [OPTIONAL] run `uvicorn backend:app --reload` to start a fast-api server on port 8000

6. run `psql -d your_database (do not specify for default) -U username (postgres) -h localhost -f path_to_your_sql_file` to fill your database with tables

7. make a post request to the server with `curl -X POST http://localhost:8000/create/user/ -d [data]` where data is or go to localhost:8000/docs to do it with a web GUI

```
`curl -X 'POST' \
  'http://localhost:8000/create/user/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "user_id": 0,
  "password": "string",
  "loyalty_card_id": 0
}'`

```


## FastApi

### Setup

1. setup python venv

2. install requirements.txt

3. for me I needed to run `pip install uvicorn[standard]` also

4. start backend server with uvicorn backend:app --reload

### Commands


. curl request at localhost:8000/docs or using

```
`curl -X 'POST' \
  'http://localhost:8000/create/user/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "user_id": 0,
  "password": "string",
  "loyalty_card_id": 0
}'`


```


## Postgres

### Initial Setup

1. Ensure you have docker installed on your distribution
   You can do this by installing docker desktop, or follow online references for all docker dependencies you need to install. We are doing this to setup a postgres container later
   
   Manual Installs if you decide not to download Docker Desktop:

        Docker Engine: https://docs.docker.com/engine/install/
        Docker Compose: https://docs.docker.com/compose/install/

3. Creating the Container

    Once you have everything installed, you can do the following

    1. Using your terminal or docker desktop (unfamiliar with this), start the container

       Enter the 'Distributed-Cafe-Loyalty-System/postgres/' directory before running any commands. Docker compose is based heavily on what directory it belongs in and even names its containers based on the folder. 

       Simply running `docker-compose up -d` or `docker compose up -d` based on your version will start the container
       
       `docker compose down` or `docker-compose down` will shut down the container

       It matters what folder the docker compose file is in. If you move it around the command might not work correctly.
       If you were in the correct folder, you should see a 'PGDATA' folder created in the postgres folder you ran the command from

    3. Checking your container is running correctly

       if you run `docker container ls` you should see something like

       ```
        CONTAINER ID   IMAGE      COMMAND                  CREATED          STATUS          PORTS                      NAMES
        2774fbe39140   postgres   "docker-entrypoint.s…"   17 seconds ago   Up 16 seconds   127.0.0.1:5432->5432/tcp   postgres-postgres-db-1

       ```

       if status does not say "up", run `docker logs [CONTAINER_ID]`, using the ID of the container, and tell me what went wrong

       As you can see in the `PORTS` field, I have mapped a port on your local machine to the container, This means you can access the database from your localhost on port 5432.

       This means any python application or sql based command line tool can be used to interact with the DB.


5. Interacting with your Database

    1. Through Docker

        If you want to access your container through docker, you can run `docker exec -it [CONTAINER_ID] /bin/bash` to start a terminal on the container. You can then run `psql -U postgres` and you should be in the database, free to run sql commands

    2. Through CLI (command-line interface) on your host machine

        Install for your environment here: https://www.timescale.com/blog/how-to-install-psql-on-mac-ubuntu-debian-windows/

        Then run the command `psql -U postgres -h localhost -p 5432`

    3. Through Python

       *ref tutorial: https://www.postgresqltutorial.com/postgresql-python/connect/, warning, do not create any new databases if u follow the tutorial*

        1. Install psycopg2 on your machine, with `pip install psycopg2`. Its good to use a python environment, if you do not know what that is, send me a message in chat.

        2. !UNTESTED BY ME AS OF NOW! Create some python file and import `import psycopg2` at the beginning.


        ```
        #Creating a connection to your postgres database

        conn = psycopg2.connect(
        host="localhost",
        database="postgres",
        user="postgres",
        )
        
        ```

        This is a reference for how to do transactions in python with our DB *https://www.postgresqltutorial.com/postgresql-python/transaction/*


3. Creating Data

    Useful website *https://www.postgresql.r2schools.com/postgresql-create-table/*

    You can check the "Basic Commands" section in part 4 of this document for more commands

    1. Creating table

    `CREATE TABLE discounts(discount_ID int, description varchar(30), PRIMARY KEY(discount))`
    -> creates a table called discount with two columns

    `DROP TABLE discount`
    -> delete a table called discount


4.  Basic Commands

    ```
    \dt - check tables
    \l - check databases
    \c [name] - connect to database called name, we use 'postgres as default'
    \dn - look at schemas (ignore this)

    SQL COMMANDS - use this website and search the sidebar for common operations - *https://www.postgresql.r2schools.com/postgresql-create-table/*

    ```

### Replication

1. When you start the containers, you can see two databases running now

```
CONTAINER ID   IMAGE         COMMAND                  CREATED        STATUS        PORTS                      NAMES
56d2ce5ea474   postgres:14   "docker-entrypoint.s…"   45 hours ago   Up 27 hours   127.0.0.1:5432->5432/tcp   postgres-postgres-db-primary-1
035e7700570e   postgres:14   "docker-entrypoint.s…"   45 hours ago   Up 27 hours   127.0.0.1:5433->5432/tcp   postgres-postgres-db-replica-1

```

2. write database is accessed at port 5432, read is at 5433

#### Commands


1. `SELECT * FROM pg_replication_slots;` -> view replication slots and their status (on primary)

2. `SELECT pg_create_physical_replication_slot('replication_slot');` creates replication slot

3. `pg_basebackup --pgdata=/var/lib/postgresql/data -R --slot=replication_slot --host=postgres-db-primary --port=5432` 




