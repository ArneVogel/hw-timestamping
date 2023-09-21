

timestamping: rx_timestamping.c
	gcc -O2 rx_timestamping.c -o timestamping

run: timestamping
	sudo ./timestamping --port 1337 --max 100000
