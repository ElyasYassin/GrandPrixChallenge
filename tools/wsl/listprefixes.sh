# list the model prefixes stored in MinIO, one per line
aws --profile minio --endpoint-url http://localhost:9000 s3 ls s3://bucket/ | awk '{print $2}' | tr -d '/'
