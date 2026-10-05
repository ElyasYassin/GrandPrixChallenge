# Grip test: drive a steady circle at a fixed steering angle and speed, record the trace.
# Copies a discrete model and sets ALL its actions to (STEER, SPEED), so the policy's choice doesn't matter.
# usage: grip_test.sh <discrete-source-snapshot> <steer-deg> <speed> [seconds=60]
SRC=$1; STEER=$2; SPEED=$3; SECS=${4:-60}; DST="cedc-grip-s${STEER}-v${SPEED}"
A="aws --profile minio --endpoint-url http://localhost:9000"
if [ -n "$(docker ps -q --filter name=deepracer-0-robomaker)" ]; then echo "training is running: not testing"; exit 3; fi
$A s3 rm --recursive --quiet s3://bucket/$DST/
$A s3 cp --recursive --quiet s3://bucket/$SRC/model/ s3://bucket/$DST/model/
$A s3 cp --quiet s3://bucket/$SRC/model/model_metadata.json /tmp/mm.json
python3 -c "
import json; d=json.load(open('/tmp/mm.json'))
d['action_space']=[{'steering_angle':float('$STEER'),'speed':float('$SPEED'),'index':i} for i in range(len(d['action_space']))]
json.dump(d,open('/tmp/mm.json','w'),indent=2)"
$A s3 cp --quiet /tmp/mm.json s3://bucket/$DST/model/model_metadata.json
EVAL_MAX_S=$SECS bash /tmp/evalrun.sh $DST Vegas_track grip/s${STEER}-v${SPEED} > /dev/null 2>&1
$A s3 rm --recursive --quiet s3://bucket/$DST/
echo "done s${STEER} v${SPEED}: $(grep -c SIM_TRACE_LOG "$(cat /tmp/gpc_root)/evals/grip/s${STEER}-v${SPEED}/robomaker.log") trace steps"
