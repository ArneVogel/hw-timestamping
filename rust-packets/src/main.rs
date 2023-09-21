extern crate libc;
extern crate packet;
use libc::{c_void, sendto, sockaddr, sockaddr_ll, socket, AF_PACKET, SOCK_RAW};
use std::fs::File;
use packet::Builder;
use std::io::Write;
use std::io::Error;
use std::time::Instant;
use std::mem;
use std::net::UdpSocket;
use std::thread;
use std::{io, net::Ipv4Addr};
use std::time::{Duration, SystemTime};

const PACKET_LEN: usize = 1024;
const UDP_PAYLOAD_SIZE: usize = 900;

/// Open a raw AF_PACKET socket
fn open_fd() -> io::Result<i32> {
    unsafe {
        match socket(AF_PACKET, SOCK_RAW, libc::AF_INET as i32) {
            -1 => Err(io::Error::last_os_error()),
            fd => Ok(fd),
        }
    }
}

fn main() {
    let other_ip = [10, 10, 1, 255];
    let my_ip = [10, 10, 1, 255];

    /* When you send packets, it is enough to specify sll_family,
     * sll_addr, sll_halen, sll_ifindex, and sll_protocol. The other
     * fields should be 0. sll_hatype and sll_pkttype are set on
     * received packets for your information. */
    let mut sa = sockaddr_ll {
        // https://man7.org/linux/man-pages/man7/packet.7.html
        sll_family: AF_PACKET as u16, // /* Always AF_PACKET */
        sll_protocol: 0x0800,         // IP packet
        sll_ifindex: 4,               // Interface number
        sll_hatype: 0,
        sll_pkttype: 0, // These types make sense only for receiving.
        sll_halen: 0,
        sll_addr: [0; 8],
    };

    let fd = open_fd().unwrap();

    let my_mac = "0c:42:a1:dd:57:30".parse().unwrap();
    let other_mac = "ff:ff:ff:ff:ff:ff".parse().unwrap();

    let payload: [&u8; UDP_PAYLOAD_SIZE] = [&65; UDP_PAYLOAD_SIZE];

    let mut p = packet::ether::Builder::default()
        .source(my_mac)
        .unwrap()
        .destination(other_mac)
        .unwrap()
        .protocol(packet::ether::Protocol::Ipv4)
        .unwrap()
        .ip()
        .unwrap()
        .v4()
        .unwrap()
        .udp()
        .unwrap()
        .source(1336)
        .unwrap()
        .destination(1337)
        .unwrap()
        .payload(payload)
        .unwrap()
        .build()
        .unwrap();

    while p.len() != PACKET_LEN {
        p.push(0);
    }

    let mut buffer: [u8; PACKET_LEN] = p.try_into().unwrap();

    // we will change the payload, so zeroing the checksum
    for i in 0..2 {
        buffer[40+i] = 0;
    }

    let total_packets = 100_000;

    for i in 0..1 {
        thread::spawn(move || {
            for i in 0..total_packets {

                let ten_millis = Duration::from_micros(200); 
                thread::sleep(ten_millis);

                let duration_since_epoch = SystemTime::now().duration_since(SystemTime::UNIX_EPOCH).unwrap(); 
                let timestamp_nanos : u64 = duration_since_epoch.as_nanos() as u64;
                for (i, byte) in timestamp_nanos.to_be_bytes().into_iter().enumerate() {
                    buffer[42+i] = byte;
                }
                unsafe {
                    let addr_ptr = mem::transmute::<*mut sockaddr_ll, *mut sockaddr>(&mut sa);
                    match sendto(
                        fd,
                        &mut buffer as *mut _ as *const c_void,
                        mem::size_of_val(&buffer),
                        0,
                        addr_ptr,
                        mem::size_of_val(&sa) as u32,
                    ) {
                        d if d < 0 => println!("Error sending: {}", Error::last_os_error()),
                        _ => continue, // great success
                    }
                }
            }
        });
    }

    let socket = UdpSocket::bind("0.0.0.0:4200").unwrap();
    let mut buf = [0; UDP_PAYLOAD_SIZE];

    let mut start = Instant::now();

    let mut latency_numbers = Vec::new();

    let mut previous_received_timestamp = 0;

    for i in 0..total_packets {
        let (num_bytes, src) = socket.recv_from(&mut buf).unwrap();

        let duration_since_epoch = SystemTime::now().duration_since(SystemTime::UNIX_EPOCH).unwrap(); 
        let timestamp_nanos : u64 = duration_since_epoch.as_nanos() as u64;

        let mut a = [0; 8];
        for i in 0..8 {
            a[i] = buf[i];
        }
        let received_timestamp : u64 = u64::from_be_bytes(a);
        if (previous_received_timestamp == received_timestamp) {
            panic!("Unlikely");
        }
        previous_received_timestamp = received_timestamp;

        let latency = timestamp_nanos - received_timestamp;
        latency_numbers.push(latency);
    }
    let mut file = File::create("end_to_end_latency.txt").unwrap();
    for n in latency_numbers {
        write!(file, "{}\n", n);
    }
}
