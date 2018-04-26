'''
CS5250 Assignment 4, Scheduling policies simulator
Sample skeleton program
Author: Minh Ho
Input file:
    input.txt
Output files:
    FCFS.txt
    RR.txt
    SRTF.txt
    SJF.txt

Apr 10th Revision 1:
    Update FCFS implementation, fixed the bug when there are idle time slices between processes
    Thanks Huang Lung-Chen for pointing out
Revision 2:
    Change requirement for future_prediction SRTF => future_prediction shortest job first(SJF), the simpler non-preemptive version.
    Let initial guess = 5 time units.
    Thanks Lee Wei Ping for trying and pointing out the difficulty & ambiguity with future_prediction SRTF.
'''
import sys
import heapq
import copy

input_file = 'input.txt'

class Process:
    last_scheduled_time = 0
    def __init__(self, id, arrive_time, burst_time):
        self.id = id
        self.arrive_time = arrive_time
        self.burst_time = burst_time
    #for printing purpose
    def __repr__(self):
        return ('[id %d : arrive_time %d,  burst_time %d]'%(self.id, self.arrive_time, self.burst_time))

def FCFS_scheduling(process_list):
    #store the (switching time, proccess_id) pair
    schedule = []
    current_time = 0
    waiting_time = 0
    for process in process_list:
        if(current_time < process.arrive_time):
            current_time = process.arrive_time
        schedule.append((current_time,process.id))
        waiting_time = waiting_time + (current_time - process.arrive_time)
        current_time = current_time + process.burst_time
    average_waiting_time = waiting_time/float(len(process_list))
    return schedule, average_waiting_time

#Input: process_list, time_quantum (Positive Integer)
#Output_1 : Schedule list contains pairs of (time_stamp, proccess_id) indicating the time switching to that proccess_id
#Output_2 : Average Waiting Time
def RR_scheduling(process_list, time_quantum ):
    input_list = copy.deepcopy(process_list)
    schedule = []
    waiting_time = 0
    wait_q = []
    N = len(input_list)
    current_process = None
    t = 0
    q_t = 0
    c_switch = False

    while True:

        while (len(input_list) != 0 and input_list[0].arrive_time <= t):
            wait_q.append(input_list.pop(0))

        if current_process == None:
            current_process = wait_q.pop(0)
            schedule.append((t, current_process.id))
            t += 1
            continue

        current_process.burst_time -= 1
        current_process.arrive_time += 1
        q_t += 1

        if(current_process.burst_time == 0):
            waiting_time += t - (current_process.arrive_time)
        elif q_t == time_quantum:
            wait_q.append(current_process)
        else:
            t += 1
            continue

        if(len(wait_q) != 0):
            if(current_process != wait_q[0]):
                c_switch = True
            current_process = wait_q.pop(0)
            q_t = 0
        elif (len(input_list) != 0):
            current_process = input_list.pop(0)
            t = current_process.arrive_time
            c_switch = True
            q_t = 0
        else:
            break

        if c_switch == True:
            schedule.append((t, current_process.id))
            c_switch = False

        t += 1

    return schedule, (waiting_time/N)

def SRTF_scheduling(process_list):
    input_list = copy.deepcopy(process_list)
    wait_q = []
    schedule = []
    N = len(input_list)
    current_process = None
    t = 0
    waiting_time = 0
    c_switch = False

    while True:

        while (len(input_list) != 0 and input_list[0].arrive_time == t):
            wait_q.append((input_list[0].burst_time, input_list[0]))
            input_list.pop(0)

        wait_q.sort(key= lambda tup: tup[0])

        if current_process == None:
            current_process = wait_q.pop(0)[1]
            schedule.append((t, current_process.id))
            t += 1
            continue

        current_process.burst_time -= 1
        current_process.arrive_time += 1

        if (current_process.burst_time == 0):
            waiting_time += (t - current_process.arrive_time)
        elif(len(wait_q) != 0 and current_process.burst_time > wait_q[0][0]):
            wait_q.append((current_process.burst_time, current_process))
        else:
            t += 1
            continue

        wait_q.sort(key= lambda tup: tup[0])

        if len(wait_q) != 0 :
            current_process = wait_q.pop(0)[1]
            c_switch = True
        else:
            if(len(input_list) == 0):
                break
            t = input_list[0].arrive_time
            while (len(input_list) != 0 and input_list[0].arrive_time == t):
                wait_q.append((input_list[0].burst_time, input_list[0]))
                input_list.pop(0)
            wait_q.sort(key= lambda tup: tup[0])
            current_process = wait_q.pop(0)[1]
            c_switch = True

        if c_switch == True:
            schedule.append((t, current_process.id))
            c_switch = False

        t += 1

    return schedule, (waiting_time/N)

def SJF_scheduling(process_list, alpha):
    input_list = copy.deepcopy(process_list)
    wait_q = []
    schedule = []
    N = len(input_list)
    current_process = None
    t = 0
    waiting_time = 0
    initial_guess = 5
    p_burst = {}

    while True:

        while (len(input_list) != 0 and input_list[0].arrive_time <= t):
            burst = p_burst.get(input_list[0].id, initial_guess)
            wait_q.append((burst, input_list[0]))
            input_list.pop(0)

        if(len(wait_q) != 0):
            wait_q.sort(key=lambda tup: tup[0])
            current_process = wait_q.pop(0)[1]
            schedule.append((t, current_process.id))
            p_burst[current_process.id] = (alpha * current_process.burst_time) + ((1-alpha) * p_burst.get(current_process.id, initial_guess))
            t += current_process.burst_time
            waiting_time += (t - (current_process.arrive_time + current_process.burst_time))
        else:
            if(len(input_list) == 0):
                break
            t = input_list[0].arrive_time
            while (len(input_list) != 0 and input_list[0].arrive_time <= t):
                burst = p_burst.get(input_list[0].id, initial_guess)
                wait_q.append((burst, input_list[0]))
                input_list.pop(0)

    return schedule, (waiting_time/N)


def read_input():
    result = []
    with open(input_file) as f:
        for line in f:
            array = line.split()
            if (len(array)!= 3):
                print ("wrong input format")
                exit()
            result.append(Process(int(array[0]),int(array[1]),int(array[2])))
    return result
def write_output(file_name, schedule, avg_waiting_time):
    with open(file_name,'w') as f:
        for item in schedule:
            f.write(str(item) + '\n')
        f.write('average waiting time %.2f \n'%(avg_waiting_time))


def main(argv):
    process_list = read_input()
    print ("printing input ----")
    for process in process_list:
        print (process)
    print ("simulating FCFS ----")
    FCFS_schedule, FCFS_avg_waiting_time =  FCFS_scheduling(process_list)
    write_output('FCFS.txt', FCFS_schedule, FCFS_avg_waiting_time )
    print ("simulating RR ----")
    RR_schedule, RR_avg_waiting_time =  RR_scheduling(process_list,time_quantum = 2)
    write_output('RR.txt', RR_schedule, RR_avg_waiting_time )
    for i in range(1, 11):
        RR_schedule, RR_avg_waiting_time =  RR_scheduling(process_list,time_quantum = i)
        print("Time quantum = " + str(i) + "  Avg_wait_time = " + str(RR_avg_waiting_time))
    print ("simulating SRTF ----")
    SRTF_schedule, SRTF_avg_waiting_time =  SRTF_scheduling(process_list)
    write_output('SRTF.txt', SRTF_schedule, SRTF_avg_waiting_time )
    print ("simulating SJF ----")
    SJF_schedule, SJF_avg_waiting_time =  SJF_scheduling(process_list, alpha = 0.5)
    write_output('SJF.txt', SJF_schedule, SJF_avg_waiting_time )
    for x in range(11):
        SJF_schedule, SJF_avg_waiting_time =  SJF_scheduling(process_list, alpha = (0.1 * x))
        print("Alpha = %.1f"%(0.1 * x) + " Avg_wait_time =" + str(SJF_avg_waiting_time))
if __name__ == '__main__':
    main(sys.argv[1:])
