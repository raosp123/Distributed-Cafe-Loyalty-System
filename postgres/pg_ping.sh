#!/bin/bash

COUNT=0
SLEEP_COUNTER=0

#runs until the primary database fails.

#if primary down for one minute (5 failures), failover. If less than 5 failures in 2 minutes, reset conditions (accounts for temporary network issues)
while [[ $COUNT -lt 5 ]]
do
    #if we have gone two minutes without 5 failures, reset the failure counters
    if [[ $SLEEP_COUNTER = 10 ]]; then SLEEP_COUNTER=0; COUNT=0; fi 

    echo -n "Liveness Check: "
    pg_isready -U postgres -h postgres-db-primary

    #If database is unreachable
    if [[ $? = 2 ]];then
        COUNT=$((COUNT+1))
        echo "Liveness Check: primary database did not respond, total attempts: $COUNT"
    fi

    sleep 12
    SLEEP_COUNTER=$((SLEEP_COUNTER+1))

done

echo "Liveness Check: Primary database has been down for more than 2 minutes, promoting Replica to primary"

if [[ $COUNT -eq 5 ]]; then

    runuser postgres -c 'pg_ctl promote -D /var/lib/postgresql/data'
    echo "Promotion Complete"

fi




