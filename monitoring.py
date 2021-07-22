import sys
import libvirt
import time
import socket
import threading

IP = '0.0.0.0'
PORT_NO = 8080
IP_vm2 = '192.168.122.3'
PORT_vm2 = 50000
DOM1_NAME = "vm1_name"
DOM2_NAME = "vm2_name"
CPU_USAGE_THRESHOLD = 85
HIGH_USAGE_ITERS_THRESHOLD = 3

# virConnectPtr handle
conn = None

# virDomainPtr handles
dom1 = None
dom2 = None

# clientMonitoringSocket
conn_client = None

def spawn_vm_and_send_message_client(n):
    """
    start a new vm and send message to client telling the new number of available servers
    n: updated no of servers available
    """

    # start vm if not already started
    if not dom2.isActive():
        if dom2.create()<0:
            print('Can not boot new vm.',file=sys.stderr)
            exit(1)
        
        print('Starting a new VM, please wait...')

        # wait for vm to boot completely and server to run
        server_up = False
        temp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        while not server_up:
            try:
                temp_socket.connect((IP_vm2, PORT_vm2))
                server_up = True
                temp_socket.close()

            except Exception:
                time.sleep(1)
                # wait for vm to boot up

    data = str(n)
    conn_client.send(data.encode())

    conn_client.close()

def connect_to_client():
    """
    connect to client to pass no of vm information
    """
    global conn_client
    serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serv.bind((IP, PORT_NO))
    serv.listen(1)
    conn_client, _ = serv.accept()


def print_cpu_usage(dom_name, usage):
    """
    print CPU usage for dom_name
    """
    if usage!=-1:
        print(dom_name[12:] + ' CPU: ' + str(round(usage,2))+'%', end='')
    else:
        print(dom_name[12:] + ' is not active', end='')


def get_cpu_usage():
    """
    return CPU usage % for dom1 and dom2
    """

    if dom1.isActive() and dom2.isActive():
        # only one vcpu so total doesn't matter
        t1 = time.time()
        cputime1_1 = int (dom1.getCPUStats(total=True)[0]['cpu_time'])
        cputime1_2 = int (dom2.getCPUStats(total=True)[0]['cpu_time'])
        time.sleep(1)
        cputime2_1 = int (dom1.getCPUStats(total=True)[0]['cpu_time'])
        cputime2_2 = int (dom2.getCPUStats(total=True)[0]['cpu_time'])
        t2 = time.time()
        usage1 = (cputime2_1-cputime1_1)*100/((t2-t1)*1e9)
        usage2 = (cputime2_2-cputime1_2)*100/((t2-t1)*1e9)
        return usage1, usage2
    else:
        # only dom1 active
        t1 = time.time()
        cputime1_1 = int (dom1.getCPUStats(total=True)[0]['cpu_time'])
        time.sleep(1)
        cputime2_1 = int (dom1.getCPUStats(total=True)[0]['cpu_time'])
        t2 = time.time()
        usage1 = (cputime2_1-cputime1_1)*100/((t2-t1)*1e9)
        usage2 = -1
        return usage1, usage2


if __name__ == "__main__":

    conn = libvirt.open('qemu:///system')

    if conn == None:
        print('Failed to open connection to qemu:///system', file=sys.stderr)
        exit(1)

    dom1 = conn.lookupByName(DOM1_NAME)
    dom2 = conn.lookupByName(DOM2_NAME)

    if dom1==None or dom2==None:
        print('Failed to get the domain object', file=sys.stderr)
        exit(1)

    num_high_iter = 0
    overload = False

    connect_client_thread = threading.Thread(target=connect_to_client)
    connect_client_thread.start()

    try:
        while True:

            # get usage of each domain
            usage1, usage2 = get_cpu_usage()

            # print CPU usage
            print_cpu_usage(DOM1_NAME, usage1)
            print('\t\t',end='')
            print_cpu_usage(DOM2_NAME, usage2)
            print()

            # check if usage is high
            if not overload and usage1>CPU_USAGE_THRESHOLD or usage2>CPU_USAGE_THRESHOLD:
                num_high_iter+=1

            # check if cpu usage continuously high
            if not overload and num_high_iter>HIGH_USAGE_ITERS_THRESHOLD:
                overload = True
                thread = threading.Thread(target=spawn_vm_and_send_message_client(2))
                thread.start()

    except KeyboardInterrupt:
        conn.close()
        exit(0)