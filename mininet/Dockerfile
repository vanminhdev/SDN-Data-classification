FROM ubuntu:20.04
USER root
# Install required packages
RUN apt-get update && \
    apt-get install -y mininet net-tools curl iputils-ping python3 python3-pip iproute2 wget unzip openvswitch-switch

RUN apt-get install -y xterm

# Install Mininet
RUN pip3 install mininet

CMD ["/bin/bash", "-c", "service openvswitch-switch start; python3 ${INIT_NET}; tail -f /dev/null"]