#!/bin/sh

set -e # exit immediately if newman complains
trap 'kill $PID' EXIT # kill the server on exit

./run.sh &
PID=$! # record the PID
newman run post_read_delete.postman_collection.json
newman run user_delete_search.postman_collection.json
newman run admin_post_delete.postman_collection.json