import sys
import md5
import socket, fcntl, struct
import redis

from config import KEY_FOR_REDIS

def disp_strategy(link_str,num_nodes,encoding="UTF-8"):
    try:
        input_str = link_str.encode(encoding,errors='ignore')
        val = int(md5.md5(input_str).hexdigest(),16)
    except UnicodeEncodeError as e:
        log.msg("encode_error_url in:%s(%s)"%(input_str,e.message),level=log.ERROR)
        return 0
    return val%num_nodes


if len(sys.argv) != 2:
    print "Usage: python inject_seeds.py SEEDS_FILE"
    sys.exit(0)

db = redis.StrictRedis(unix_socket_path="/tmp/redis.sock")

#ifname = "eth1"
#s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#inet = fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s', ifname[:15]))  
#local_ip = socket.inet_ntoa(inet[20:24])
f = open('/etc/sysconfig/network-scripts/ifcfg-enp8s0','r')
while True:
    line = f.readline()
    if not line:
        break
    if line.startswith('IPADDR'):
        ip = line.split('=')[1].strip('\n')
        break
local_ip = ip
host_conf_file = "./hosts.conf";
idx_self = -1
idx_total = 0

fin = open(host_conf_file,"r")
for line in fin:
    line = line.strip()
    if not line:
        continue
    idx_total += 1
    if line == local_ip:
        idx_self = idx_total -1
fin.close()

if idx_self == -1:
    print "my ip is not found in hosts.conf"
    sys.exit(0)

fin = open(sys.argv[1],"r")
cnt = 0
plist0 = 'plist0'+KEY_FOR_REDIS
for line in fin:
    line = line.strip()
    idx = disp_strategy(line,idx_total,)
    if idx == idx_self:
        db.zadd(plist0,0,line)
        #print line
        cnt += 1
fin.close()

print "inject ", cnt , " pages"

