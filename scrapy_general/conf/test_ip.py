import socket, fcntl, struct
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
inet = fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s', 'enp8s0'))
ip = socket.inet_ntoa(inet[20:24])
print ip
