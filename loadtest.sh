#!/bin/bash

# Define the URL you want to make requests to
url="https://www.reallygreatfeedback.com/events/58c8dfa2-f991-45a9-9c4d-d8d8a6ed86c7"

# Define the number of concurrent requests
concurrency=1000

# Define a function to make a single request
make_request() {
    echo "start"
    curl -s -o /dev/null -w "%{http_code}\n" "$url" &
    echo "finish"
}

# Loop to make concurrent requests
for ((i=1; i<=$concurrency; i++)); do
    make_request
done

# Wait for all requests to finish
wait

echo "All requests completed"

