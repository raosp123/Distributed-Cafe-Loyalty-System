#!/bin/bash

echo "hello"

set -x

if [[ -n $DATABASE_TYPE ]]; then

	echo "you made it here, $DATABASE_TYPE "

    if [[ "$DATABASE_TYPE" = 'primary' ]] ; then
        echo "Setting up initial DB"

        exec docker-entrypoint.sh postgres -c config_file=/etc/postgresql/postgresql.conf -c hba_file=/etc/postgresql/pg_hba.conf

        #run primary replication slot scripts

    elif [[ "$DATABASE_TYPE" = "replica" ]]; then

	    echo "hello2"
        # if replica hasn't been initialized already
        if [[ -z "$(ls -A /var/lib/postgresql/data/)" ]] ; then

            until pg_basebackup --pgdata=/var/lib/postgresql/data -R -U postgres --slot=replication_slot --host=postgres-db-primary --port=5432
            do
                echo 'waiting for primary to startup'
                sleep 3
            done
            echo 'Replica initialized, starting database now'  

            #start pg_test script here - checks constantly if primary is up
            chmod +x /opt/pg_ping.sh
            ./opt/pg_ping.sh &

        fi

        exec docker-entrypoint.sh postgres -c config_file=/etc/postgresql/postgresql.conf
                    


    elif [[ "$DATABASE_TYPE" = "shard" ]]; then
        echo "do something"

    fi
fi
