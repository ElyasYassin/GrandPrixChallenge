# per-episode direction (from yaw vs waypoint progress) and mean reward per step, first N episodes
R=$(docker ps -q --filter name=robomaker | head -1)
until [ "$(docker logs $R 2>&1 | grep -c 'Training>')" -ge ${1:-8} ]; do sleep 5; done
docker logs $R 2>&1 | grep SIM_TRACE_LOG | python3 -c "
import sys, collections
eps=collections.defaultdict(list)
for l in sys.stdin:
    f=l.split('SIM_TRACE_LOG:')[1].strip().split(',')
    s=[k for k,x in enumerate(f) if x in ('in_progress','off_track','lap_complete','reversed')]
    if not s: continue
    i=s[0]; eps[int(f[0])].append((int(f[i-3]), float(f[i-7]), float(f[i-4])))
for e in sorted(eps)[:${1:-8}]:
    st=eps[e]; wps=[w for w,_,_ in st]
    d=sum(1 for a,b in zip(wps,wps[1:]) if (b-a)%150 in range(1,20)) - sum(1 for a,b in zip(wps,wps[1:]) if (a-b)%150 in range(1,20))
    print(f'episode {e}: {\"waypoints increasing\" if d>0 else \"waypoints DEcreasing\"}, steps {len(st)}, mean reward/step {sum(r for _,r,_ in st)/len(st):.2f}, progress {st[-1][2]:.0f}%')
"
