# wait for N simulator steps, then show reward errors (if any) and the reward range seen
R=$(docker ps -q --filter name=deepracer-0-robomaker | head -1)
until [ "$(docker logs $R 2>&1 | grep -c SIM_TRACE_LOG)" -ge ${1:-300} ]; do sleep 5; done
docker logs $R 2>&1 | grep -iE "Traceback|reward_function.*rror|NameError|TypeError|KeyError" | head -5 | cut -c1-200
docker logs $R 2>&1 | grep SIM_TRACE_LOG | python3 -c "
import sys
rw=[];st=[]
for l in sys.stdin:
    f=l.split('SIM_TRACE_LOG:')[1].strip().split(',')
    s=[k for k,x in enumerate(f) if x in ('in_progress','off_track','lap_complete','reversed')]
    if s: rw.append(float(f[s[0]-7])); st.append(f[s[0]])
print(f'steps {len(rw)}: reward min {min(rw):.2f} median {sorted(rw)[len(rw)//2]:.2f} max {max(rw):.2f}; laps {st.count(\"lap_complete\")}')"
