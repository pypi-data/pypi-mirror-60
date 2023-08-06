LIGGGHTSER is a program that is able to automatically deal with data file printed or dumped by LIGGGHTS software, now we add some useful function like automatically get information from remote server.

Auther: Di

E-mail: wangdi931010@gmail.com

Github: https://github.com/DiWang1010

------------------About read files------------------------

To read files:

import LIGGGHTSER

reader=LIGGGHTSER.read.Read()

#To get all files in directory

filedict=reader.read_file('./')

#To get dumpfile data

dumpdata=reader.read_dump('./dump10000.ouput')

print(dumpdata['HEADER'])

print(dumpdata['id'])

print(dumpdata['type'])

pritn(dumpdata['x'])

#To read ave file

avedata=reader.read_ave('./ave_force.txt')

print(avedata['TimeStep'])

#To read thermo in log file

logdata=reader.read_log_thermo('./log.liggghts')

print(logdata['data1'])

print(logdata['data2'])

#To write dump after change some parameters

writer = LIGGGHTSER.write.Write()
dumpdata=reader.read_dump('./dump10000.ouput')
for i in range(len(dump['id'])
	dump['DATA'][i][0]=0  //when id is the first column
writer.write_dump(dumpdata,filename)

------------------About remoter server------------------------
#To ssh with remote server

cl=LIGGGHTSER.ob.ob('192.168.0.1','username','password')

Please replace the ip with your remote server, then the username and password. Port is set to 22.
#To set your email

email=cl.email_set('send@gmail.com','password','smtp.gmail.com',587,'target@mail.com',True)

If this work, then the target mailbox will receive a test email. Then you can change the last parameter to False or delete it.
#To get information by squeue command

cl.squeue()

#To automatically check your job by using jobID

jobid=[1,2,3,4,5]
cl.monitor(jobid,time_gap_by_second,email,None)

If you want to send email, copy what you got from email_set function to email. Please keep the last parameter as None for now
