package vn.edu.huce.dataclassification;

import java.nio.charset.StandardCharsets;

import org.onlab.packet.*;
import org.onosproject.net.ConnectPoint;
import org.onosproject.net.DeviceId;
import org.onosproject.net.HostId;
import org.onosproject.net.PortNumber;
import org.onosproject.net.packet.InboundPacket;
import org.onosproject.net.packet.PacketContext;
import org.onosproject.net.packet.PacketProcessor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.ObjectWriter;
import shaded.org.apache.http.protocol.HTTP;

public class MyPacketProcessor implements PacketProcessor {
    private final Logger log = LoggerFactory.getLogger(getClass());

    @Override
    public void process(PacketContext context) {
        // Xử lý gói tin ở đây
        var parsed = context.inPacket().parsed();
        var className = parsed.getClass().getTypeName();
        InboundPacket pkt = context.inPacket();
        Ethernet ethPacket = pkt.parsed();
        short etherType = ethPacket.getEtherType();

        if (etherType == Ethernet.TYPE_LLDP) {
            ConnectPoint receivedFrom = pkt.receivedFrom();
            DeviceId deviceId = receivedFrom.deviceId();
            PortNumber portNumber = receivedFrom.port();
            MacAddress sourceMac = ethPacket.getSourceMAC(); //địa chỉ mac source
            MacAddress destMac = ethPacket.getDestinationMAC(); //địa chỉ mac dest
            log.info("Received LLDP packet: From device = {}, from port = {}, source MAC = {}, destination MAC = {}",
                    deviceId, portNumber, sourceMac, destMac);
        } else if (etherType == Ethernet.TYPE_IPV4) {
            IPv4 ipv4Payload = (IPv4) ethPacket.getPayload();

            int sourceAddress = ipv4Payload.getSourceAddress();
            int destinationAddress = ipv4Payload.getDestinationAddress();

            String sourceIpAddress = IPv4.fromIPv4Address(sourceAddress);
            String destinationIpAddress = IPv4.fromIPv4Address(destinationAddress);

            // Kiểm tra giao thức Transport (TCP hoặc UDP)
            byte protocol = ipv4Payload.getProtocol();
            log.info("Received IPV4 packet from {} to {} with protocol {}",
                    sourceIpAddress, destinationIpAddress, protocol);
            if (protocol == IPv4.PROTOCOL_ICMP) {
                ICMP payload = (ICMP) ipv4Payload.getPayload();
            } else if (protocol == IPv4.PROTOCOL_TCP) {
                // Phân tích header TCP
                TCP payload = (TCP) ipv4Payload.getPayload();
                byte[] data = payload.serialize();
                //payload.setDataOffset(payload.getDataOffset());
                String text = new String(data, StandardCharsets.UTF_8);
                // Kiểm tra cổng nguồn và cổng đích
                int srcPort = payload.getSourcePort();
                int dstPort = payload.getDestinationPort();
            } else if (protocol == IPv4.PROTOCOL_UDP) {
                UDP payload = (UDP) ipv4Payload.getPayload();
            }
        }
    }
}
