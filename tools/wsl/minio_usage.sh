# where MinIO's disk use is (bucket data vs. internal trash/tmp)
cd ~/deepracer-for-cloud/data/minio && du -sh bucket .minio.sys .minio.sys/tmp 2>/dev/null; ls bucket | wc -l
