# fixed commanded speed on a long straight: every action = SPEED m/s; how fast does the car really go?
SRC=$1; SPEED=$2; DST="cedc-speedcap-fixed$SPEED"
A="aws --profile minio --endpoint-url http://localhost:9000"
$A s3 rm --recursive s3://bucket/$DST/ > /dev/null 2>&1
$A s3 cp --recursive s3://bucket/$SRC/model/ s3://bucket/$DST/model/ > /dev/null
$A s3 cp s3://bucket/$SRC/model/model_metadata.json /tmp/mm.json > /dev/null
python3 -c "import json;d=json.load(open('/tmp/mm.json'));d['action_space']['speed']={'low':float('$SPEED')-0.1,'high':float('$SPEED')};json.dump(d,open('/tmp/mm.json','w'),indent=2);print('action space:',d['action_space'])"
$A s3 cp /tmp/mm.json s3://bucket/$DST/model/model_metadata.json > /dev/null
bash /tmp/evalrun.sh $DST Straight_track speedcap-straight-$SPEED | tail -1
