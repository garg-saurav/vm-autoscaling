# vm-autoscaling
Cloud management system using the libvirt API

## Monitoring
- Continuous monitoring of CPU utilisation by server VMs
- usage % = 100 * (cpu_time 2 - cpu_time 1) / (time 2 - time 1)
- Overload if cpu usage above a threshold for some number of consecutive iterations

## Autoscaling
- Scale up from N to N+1 server vms using libvirt api
- Notify the client to use the new vm to mitigate overload

## Setting up
- Install virt-manager, libvirtd, qemu and virsh
- Use virt-manager to create two VMs 
- Configure network using steps given in [config](./conf.txt) file
- Add server code files to respective vms and configure them to run on boot up
- Start vm1 and run `python monitoring.py` and `python client.py`
- Monitoring will show cpu usage in real time
- Change load using 'C' key in the terminal where client.py is running to see autoscaling in action
