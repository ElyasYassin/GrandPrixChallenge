# Does the simulator cap the car's speed? Copy a trained checkpoint into a test run whose action
# space allows up to MAX m/s, evaluate it on Vegas, and let tools/grip_from_logs.py / the trace
# show the actual speed reached.
# usage: speedcap_test.sh <source-snapshot-prefix> <max-speed>
SRC=$1; MAX=$2; DST="cedc-speedcap-$MAX"
A="aws --profile minio --endpoint-url http://localhost:9000"
$A s3 rm --recursive s3://bucket/$DST/ > /dev/null 2>&1
$A s3 cp --recursive s3://bucket/$SRC/model/ s3://bucket/$DST/model/ > /dev/null
$A s3 cp s3://bucket/$SRC/model/model_metadata.json /tmp/mm.json > /dev/null
python3 -c "import json;d=json.load(open('/tmp/mm.json'));d['action_space']['speed']['high']=float('$MAX');json.dump(d,open('/tmp/mm.json','w'),indent=2);print('action space:',d['action_space'])"
$A s3 cp /tmp/mm.json s3://bucket/$DST/model/model_metadata.json > /dev/null
bash /tmp/evalrun.sh $DST Vegas_track speedcap-$MAX | tail -1
