# hw-timestamping

Largely based on: [https://github.com/majek/openonload/blob/master/src/tests/onload/hwtimestamping/rx_timestamping.c](https://github.com/majek/openonload/blob/master/src/tests/onload/hwtimestamping/rx_timestamping.c)

## Prerequisites

- `make`
- linuxptp: `sudo apt install linuxptp`
- rust: `sudo apt install cargo`

## Usage

Build with `make` run with `make run`.

Before the tool is run the time the time between the kernel and the NIC has to be synchronized with `phc2sys`: `sudo phc2sys -s enp65s0f0np0 -O 0 -m`

`phc2sys` must run in the background for the whole experiment.
`phc2sys` is avaliable in the linux PTP tools (`linuxptp` package mentioned above). You can also find its source code at `git://git.code.sf.net/p/linuxptp/code`

`hw-timestamping` listens for UDP packets.
The Rust application in `./rust-packets` can be used to create these packets: `cd rust-packets; cargo build --release`.
By default, the application assumes `eth0` to be the interface you want to use:
```$ sudo cargo run --release # will use eth0```

You can pass the name of the interface you want to use as the first argument:
```$ sudo cargo run --release enp65s0f0np0 # will use enp65s0f0np0```

The result of the experiment is a file with all the measured latency numbers called `latency.txt`.
Use the python script `summarize.py` to create a plot of the numbers.

## Background

[Slides](https://events.static.linuxfound.org/sites/events/files/slides/lcjp14_ichikawa_0.pdf) for PTP tools

