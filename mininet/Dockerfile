FROM ubuntu:20.04
USER root
# Install required packages
RUN apt-get update && \
    apt-get install -y mininet net-tools curl iputils-ping python3 python3-pip iproute2 wget unzip openvswitch-switch

RUN apt-get install -y xterm nano iptables

RUN apt-get install -y tcpreplay
RUN apt-get install -y tcpdump
RUN apt-get install -y iperf3
RUN apt-get install -y d-itg

# Install Mininet
RUN pip3 install mininet
RUN pip3 install Flask
RUN pip3 install opencv-python
RUN pip3 install pygame
RUN pip3 install Wave
RUN pip3 install requests
RUN pip3 install beautifulsoup4
# RUN pip3 install PyAudio

RUN apt install -y libglib2.0-0

CMD ["/bin/bash", "-c", "service openvswitch-switch start; python3 ${INIT_NET}; tail -f /dev/null"]