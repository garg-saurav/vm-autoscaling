import socket

NUM_ITERATIONS = int(1e6)
IP = '192.168.122.3'
PORT_NO = 50000
WAITING_QUEUE = 2

try:

    serv = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    serv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serv.bind((IP,PORT_NO))
    serv.listen(WAITING_QUEUE)

    while True:
        conn, addr = serv.accept()
        
        # cpu intensive task
        ret = 0
        for i in range(NUM_ITERATIONS):
            # keep CPU busy
            ret += i

        data = str(ret)+': ran for '+str(NUM_ITERATIONS)+' iterations'
        
        conn.send(data.encode())

        conn.close()

except Exception as e:
    conn.close()
    raise(e)

