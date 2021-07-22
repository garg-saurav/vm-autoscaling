import socket
import threading
import time
from enum import Enum

IP = ['192.168.122.2','192.168.122.3']
PORT_NO = 50000
IP_monitoring = '0.0.0.0'
PORT_NO_monitoring = 8080
NUM_THREADS_HIGH = 3 # no of threads in high load
NUM_THREADS_LOW = 1 # no of threads in low load
WAITING_TIME = 0.2 # time to wait bwteen consecutive threads spawning

NUM_ACTIVE_IP = 1 # no of IPs available
num_active_ip_lock = threading.Lock()
vm_index = 0 # choose index of IP to send request based on vm_index%NUM_AVAILABLE

HIGH_LOAD = False # boolean denoting whether the load is high or not
high_load_lock = threading.Lock()

def change_load(lock):
    """
    lock: synchronised access to HIGH_LOAD
    change the load from high to low and vice versa on every 'C' key press
    """
    global HIGH_LOAD

    while(True):
        inp = input()
        if(inp=='C'):
            lock.acquire()
            HIGH_LOAD = not(HIGH_LOAD)
            lock.release()

def send_request(lock, n):
    """
    lock: synchronised access to NUM_ACTIVE_IP
    n: 
    """
    lock.acquire()
    index = n%NUM_ACTIVE_IP
    lock.release()

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((IP[index], PORT_NO))
    client.recv(1024)
    client.close()

def spawn_threads(n):
    """
    n: no of threads to spawn
    """
    threads = []
    global vm_index

    # create threads
    for _ in range(n):
        vm_index+=1
        threads.append(threading.Thread(target=send_request, args=(num_active_ip_lock, vm_index)))

    # start threads
    for t in threads:
        t.start()

    # # wait for threads to finish
    # for t in threads:
    #     t.join()

    time.sleep(WAITING_TIME)


def generate_load(lock):
    """
    lock: synchronised access to HIGH_LOAD
    generate threads to spawn threads which generate load by sending requests to server
    """

    # get load from HIGH_LOAD variable
    lock.acquire()
    high_load = HIGH_LOAD
    lock.release()
    if(not (high_load)):
        print("--------Entering low load mode-------")
    else:
        print("--------Entering high load mode-------")

    num_iters = 0

    while True:
        num_iters+=1
        prev_load = high_load
        lock.acquire()
        high_load = HIGH_LOAD
        lock.release()
        if prev_load!=high_load:
            if(not (high_load)):
                print("--------Entering low load mode-------")
            else:
                print("--------Entering high load mode-------")

        if high_load:
            spawn_threads(NUM_THREADS_HIGH)
        else:
            spawn_threads(NUM_THREADS_LOW)
        
def listen_monitoring():
    """
    listen to monitoring script for change in no of IPs
    """
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    while True:

        try:
            client.connect((IP_monitoring,PORT_NO_monitoring))  
            from_monitoring = client.recv(4).decode()
            new_num_active = int(from_monitoring)
            client.close()

            print("Update: Another VM up and running!")

            num_active_ip_lock.acquire()
            global NUM_ACTIVE_IP
            NUM_ACTIVE_IP = new_num_active
            num_active_ip_lock.release()

        except Exception:
            time.sleep(1)


if __name__ == "__main__":

    # create generate load thread and monitoring listening thread
    load_thread = threading.Thread(target=generate_load,args=(high_load_lock,))
    listen_monitoring_thread = threading.Thread(target=listen_monitoring)
    setting_high_load_thread = threading.Thread(target=change_load,args=(high_load_lock,))

    # start threads
    load_thread.start()
    listen_monitoring_thread.start()
    setting_high_load_thread.start()

    # wait until load threads finish
    while(True):
        time.sleep(1)
