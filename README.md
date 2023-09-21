# hw-timestamping

Largely based on: [https://github.com/majek/openonload/blob/master/src/tests/onload/hwtimestamping/rx_timestamping.c](https://github.com/majek/openonload/blob/master/src/tests/onload/hwtimestamping/rx_timestamping.c)

## Usage

Build with `make` run with `make run`.

Before the tool is run the time the time between the kernel and the NIC has to be synchronized with `phc2sys`: `sudo ./phc2sys -s enp65s0f0np0 -O 0 -m`

`phc2sys` must run in the background for the whole experiment.
`phc2sys` is avaliable from the linux PTP tools which is available at: git://git.code.sf.net/p/linuxptp/code

`hw-timestamping` listens for UDP packets.
The Rust application in `./rust-packets` can be used to create these packets.

The result of the experiment is a file with all the measured latency numbers called `latency.txt`.
Use the python script `summarize.py` to create a plot of the numbers.

## Background

[Slides](https://events.static.linuxfound.org/sites/events/files/slides/lcjp14_ichikawa_0.pdf) for PTP tools 


