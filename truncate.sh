#!/bin/bash

for tbl in prod seq job db
do
    echo "DELETE FROM $tbl;" | sqlite3 deciphon.sched
done
