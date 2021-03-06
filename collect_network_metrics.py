#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 10 22:14:42 2019

@author: masudulhasanmasudb
"""
import subprocess,time
import os
import subprocess, time
from subprocess import PIPE, Popen
import threading

class fileWriteThread(threading.Thread):
    def __init__(self, metric_string):
        threading.Thread.__init__(self)
        self.metric_string = metric_string

    def run(self):
        output_file = open("tcp_metrics.txt","a+")
        output_file.write(str(self.metric_string))
        output_file.flush()
        output_file.close()


proc = Popen(['ls', '-l', '/proc/fs/lustre/osc'], universal_newlines=True, stdout=PIPE)
res = proc.communicate()[0]
parts = res.split("\n")
for x in range(1, len(parts)):
    ost_name_parts = parts[x].split(" ")
    if "panda-OST0009" in ost_name_parts[len(ost_name_parts) - 1]:
        OST_name = ost_name_parts[len(ost_name_parts) - 1]
        break
ost_path = '/proc/fs/lustre/osc/' + OST_name
#print(ost_path)        



src_ip = "134.197.40.134"
dst_ip = "192.231.243.54"
comm_ss = ['ss', '-t', '-i', 'state', 'ESTABLISHED', 'dst', dst_ip]
is_controller_port = True

total_string = ""
start = time.time()
initial_time = time.time()
total_rtt_value = 0
total_pacing_rate = 0
is_first_time = True
prev_req_wait_time = -1
avg_wait_time = 0
total_wait_time = 0
total_cwnd_value = 0
total_rto_value = 0
byte_ack = 0
byte_ack_so_far = 0
segs_out = 0
seg_out_so_far = 0
retrans = 0
ssthresh =0
total_ost_read = 0

prev_active_req = -1
prev_ost_read = -1
avg_req_number = 0
total_req_number = 0
total_pending_page = 0
total_pending_rpc = 0

time_diff = 0
epoc_time = 0
has_transfer_started = False

out_file = open("dataset.csv","a+")

while(1):
    ss_proc = subprocess.Popen(comm_ss, stdout=subprocess.PIPE)
    line_in_ss = str(ss_proc.stdout.read())
    if line_in_ss.count("192.231.243.54")==2:
        if (is_first_time):
            initial_time = time.time()
            is_first_time = False
            has_transfer_started = True
    
        parts = line_in_ss.split("\n")
#        print(parts)
#        p_time = time.time()
#        time_diff = float(p_time - initial_time)
        time_diff+=1
        epoc_time+=1
#        print(time_diff)
        for x in range(len(parts)):
    #        print(parts[x])
        #    print(line_in_ss)
    #        print(is_controller_port)
            if "192.231.243.54" in parts[x] and "gsiftp" not in parts[x]:
                if (is_first_time):
                    initial_time = time.time()
                    is_first_time = False
                
                metrics_line = parts[x+1].strip("\\t").strip()
                metrics_parts = metrics_line.split(" ")
        #        print(metrics_parts)
                for y in range(len(metrics_parts)):
                    if "rtt" in metrics_parts[y]:
                        s_index = metrics_parts[y].find(":")
                        e_index = metrics_parts[y].find("/")
                        value = float(metrics_parts[y][s_index+1:e_index])
    #                    print("RTT "+str(value))
                        total_rtt_value+=value
#                        print("avg RTT "+str(avg_rtt_value))
#                        avg_value = avg_rtt_value/time_diff
#                        print("RTT "+str(avg_value))
                        
                    if "pacing_rate" in metrics_parts[y]:
                        index = metrics_parts[y+1].find("Mbps")
                        p_rate = float(metrics_parts[y+1][:index])
                        total_pacing_rate+=p_rate
#                        print("avg pacing rate "+str(avg_pacing_rate))
#                        p_avg_value = avg_pacing_rate/time_diff
#                        print("pacing rate "+ str(p_avg_value))
                        
                    if "cwnd" in metrics_parts[y]:
                        s_index = metrics_parts[y].find(":")
                        value = float(metrics_parts[y][s_index+1:])
                        total_cwnd_value+=value
                    
                    if "rto" in metrics_parts[y]:
                        s_index = metrics_parts[y].find(":")
                        value = float(metrics_parts[y][s_index+1:])
                        total_rto_value+=value
                    
                    if "bytes_acked" in metrics_parts[y]:
                        s_index = metrics_parts[y].find(":")
                        value = float(metrics_parts[y][s_index+1:])
#                        print("byte ack "+str((value-byte_ack_so_far)))
                        byte_ack+=(value-byte_ack_so_far)
                        byte_ack_so_far = value
                        
                    if "segs_out" in metrics_parts[y]:
                        s_index = metrics_parts[y].find(":")
                        value = float(metrics_parts[y][s_index+1:])
#                        print("seg out "+str((value-seg_out_so_far)))
                        segs_out+=(value-seg_out_so_far)
                        seg_out_so_far = value
                    
                    if "retrans" in metrics_parts[y]:
                        s_index = metrics_parts[y].find(":")
                        e_index = metrics_parts[y].find("/")
                        value = float(metrics_parts[y][s_index+1:e_index])
                        retrans += value
                        
#                    if "ssthresh" in metrics_parts[y]:
#                        s_index = metrics_parts[y].find(":")
#                        value = float(metrics_parts[y][s_index+1:])
#                        ssthresh+=value    
#                           
                    
                        
        
#    total_string+=time.ctime() + "\n"
#    total_string+=str(line_in_ss)+"\n\n"
#    now = time.time()
#    difference = int(now - start)
#    if(difference>=10):
#        thread1 = fileWriteThread(total_string)
#        thread1.start()
#        total_string =""
#        start = now
#    else:
#        if(has_transfer_started):
#            break            
                            
    
                      
                    
    proc = Popen(['cat', ost_path+"/stats"], universal_newlines=True, stdout=PIPE)
    res = proc.communicate()[0]
#    print(res)
    res_parts = res.split("\n")
#    print(res_parts)
    for metric_line in res_parts:
        if "req_waittime" in metric_line:
            tokens = str(metric_line).split(" ")
#            print(tokens)
            wait_time = float(tokens[len(tokens)-2])
            if (time_diff ==1 and prev_req_wait_time == -1):
                prev_req_wait_time = wait_time
            elif(time_diff>1):    
                diff = wait_time - prev_req_wait_time
#                print("diff " + str(diff))
                total_wait_time+=(diff/(1000000))
#                avg_wait_time = total_wait_time/time_diff
#                print("wait time "+str(avg_wait_time))
                prev_req_wait_time = wait_time
                
                
        if "req_active" in metric_line:
            tokens = str(metric_line).split(" ")
#            print(tokens)
            req_number = float(tokens[len(tokens)-2])
            if (time_diff ==1 and prev_active_req== -1):
                prev_active_req = req_number
            elif(time_diff>1):    
                diff = req_number - prev_active_req
#                print("req diff " + str(diff))
                total_req_number+= diff
#                avg_req_number = total_req_number/time_diff
#                print("req number "+str(avg_req_number))
                prev_active_req = req_number
                
        if "ost_read" in metric_line:
            tokens = str(metric_line).split(" ")
#            print(tokens)
            ost_read = float(tokens[len(tokens)-2])
            if (time_diff ==1 and prev_ost_read == -1):
                prev_ost_read = ost_read
            elif(time_diff>1):    
                diff = ost_read - prev_ost_read
#                print("ost_read diff " + str(diff))
                total_ost_read+= (diff/(1000000))
#                avg_ost_read = total_ost_read/time_diff
#                print("ost_read "+str(avg_ost_read))
                prev_ost_read = ost_read         
                
     
    proc = Popen(['cat', ost_path+"/rpc_stats"], universal_newlines=True, stdout=PIPE)
    res = proc.communicate()[0]
#    print(res)
    res_parts = res.split("\n")
#    print(res_parts)
    for metric_line in res_parts:
        if "pending read pages" in metric_line:
            index = metric_line.find(":")
            value = float(metric_line[index+1:])
            total_pending_page+=value
#            if time_diff>=1:
#                print("pending read pages: "+str(value))
#                print("avg pending read pages: "+str(total_pending_page/time_diff))
        
        if "read RPCs in flight" in metric_line:
            index = metric_line.find(":")
            value = float(metric_line[index+1:])
            total_pending_rpc+=value
#            if time_diff>=1:
#                print("pending total_pending_rpc: "+str(value))
#                print("avg pending total_pending_rpc: "+str(total_pending_rpc/time_diff)) 
                
    if(time_diff>=10):
    
        avg_rtt_value = total_rtt_value/time_diff
        p_avg_value = total_pacing_rate/time_diff
        
        avg_cwnd_value = total_cwnd_value/time_diff
        avg_rto_value = total_rto_value/time_diff
        
        avg_byte_ack = byte_ack/(1024*1024)
        avg_seg_out = segs_out
        avg_retrans = retrans/time_diff
#        avg_ssthresh = ssthresh/time_diff
        
        avg_wait_time = total_wait_time/time_diff
        avg_req_number = total_req_number/time_diff
        avg_pending_page = total_pending_page/time_diff
        avg_rpc = total_pending_rpc/time_diff
        
        is_network_normal = False
        is_disk_normal = False
        avg_ost_read = total_ost_read/time_diff
    
        if (avg_rtt_value < 62 and p_avg_value>10000 and avg_cwnd_value>4000 and avg_rto_value<265 and avg_byte_ack >300 and avg_seg_out>40000 and avg_retrans==0):
            is_network_normal = True
        
        if (avg_wait_time<6 and avg_req_number<500 and avg_ost_read<6 and avg_pending_page<1024 and avg_rpc < 4):
            is_disk_normal = True
        
#        normal = 0
#        network = 1
#        disk =2
#        both = 3
        
        if(is_disk_normal and is_network_normal):
            result_value = 0
        elif(not is_disk_normal and not is_network_normal):
            result_value = 3
        elif(is_network_normal):
            result_value = 2
        else:
            result_value = 1
        
        
        time_diff = 0
        
        total_rtt_value = 0
        total_pacing_rate = 0
        total_wait_time = 0
        total_cwnd_value = 0
        total_rto_value = 0
        byte_ack = 0
        segs_out = 0
        retrans = 0
        total_ost_read = 0
        total_req_number = 0
        total_pending_page = 0
        total_pending_rpc = 0
    
    
    
        
        
#        print("rtt = "+str(avg_rtt_value)+" pacing_rate = "+str(p_avg_value) + " cwnd = "+str(avg_cwnd_value)+" rto = "+str(avg_rto_value))  
#        print("byte ack = "+str(avg_byte_ack/(1024*1024))+" seg out = "+str(avg_seg_out) + " Retrans = "+str(retrans))

        print("result value = "+str(result_value))
        if result_value!=3:
            out_file.write(str(avg_rtt_value)+","+str(p_avg_value) + ","+str(avg_cwnd_value)+","+str(avg_rto_value)+",")
            out_file.write(str(avg_byte_ack)+","+str(avg_seg_out) + ","+str(retrans)+",")
            out_file.write(str(avg_wait_time)+","+str(avg_req_number) + ","+str(avg_ost_read)+","+str(avg_pending_page)+","+str(avg_rpc)+",")
            out_file.write(str(result_value)+"\n")
            out_file.flush()        
                
                
#    out_file.write(time.ctime() + "\n")
#    out_file.write(res)
#    out_file.write("\n\n\n")
#    out_file.flush()
                
#    if(epoc_time==5):
#        avg_rtt_value = total_rtt_value/epoc_time
#        avg_rto_value = total_rto_value/epoc_time
#        
#        avg_wait_time = total_wait_time/epoc_time
#        avg_pending_page = total_pending_page/epoc_time
#        
#        
#        print("rtt = "+str(avg_rtt_value)+" rto = "+str(avg_rto_value))  
                
                
        
        
    time.sleep(.1)
    
    

  