O="/mnt/c/Users/Elyas/OneDrive - The University of Colorado Denver/Desktop/projects/GrandPrixChallenge/models/$1/model"
mkdir -p "$O"
aws --profile minio --endpoint-url http://localhost:9000 s3 cp --recursive s3://bucket/$1/model/ "$O/" > /dev/null
ls -la "$O" | tail -n +2
