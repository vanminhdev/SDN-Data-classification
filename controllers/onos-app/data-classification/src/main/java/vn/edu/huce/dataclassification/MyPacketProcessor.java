package vn.edu.huce.dataclassification;

import org.onlab.packet.*;
import org.onlab.packet.TCP;
import org.onosproject.net.ConnectPoint;
import org.onosproject.net.DeviceId;
import org.onosproject.net.PortNumber;
import org.onosproject.net.packet.InboundPacket;
import org.onosproject.net.packet.PacketContext;
import org.onosproject.net.packet.PacketProcessor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import vn.edu.huce.dataclassification.dtos.data.DataFlowDto;
import vn.edu.huce.dataclassification.utils.ApiClient;
import vn.edu.huce.dataclassification.utils.DateTimeUtil;

import java.nio.charset.StandardCharsets;

public class MyPacketProcessor implements PacketProcessor {
    private final Logger log = LoggerFactory.getLogger(getClass());
    private final ApiClient apiClient = new ApiClient();

    public static final short FIN = 0b0000000000000001;
    public static final short SYN = 0b0000000000000010;
    public static final short RST = 0b0000000000000100;
    public static final short PSH = 0b0000000000001000;
    public static final short ACK = 0b0000000000010000;
    public static final short URG = 0b0000000000100000;
    public static final short ECE = 0b0000000001000000;
    public static final short CWR = 0b0000000010000000;

    @Override
    public void process(PacketContext context) {
        // Xử lý gói tin ở đây
        // var parsed = context.inPacket().parsed();
        InboundPacket pkt = context.inPacket();
        Ethernet ethPacket = pkt.parsed();

        short etherType = ethPacket.getEtherType();
        short flags = 0;

        MacAddress sourceMac = ethPacket.getSourceMAC(); // địa chỉ mac source
        MacAddress destMac = ethPacket.getDestinationMAC(); // địa chỉ mac dest

        ConnectPoint receivedFrom = pkt.receivedFrom();
        DeviceId deviceId = receivedFrom.deviceId();
        PortNumber portNumber = receivedFrom.port();
        long timestamp = context.time();

        if (etherType == Ethernet.TYPE_LLDP) {
            // log.info("Received LLDP packet: From device = {}, from port = {}, source MAC
            // = {}, destination MAC = {}",
            // deviceId, portNumber, sourceMac, destMac);
        } else if (etherType == Ethernet.TYPE_IPV4) {
            IPv4 ipv4Payload = (IPv4) ethPacket.getPayload();

            int sourceAddress = ipv4Payload.getSourceAddress();
            int destinationAddress = ipv4Payload.getDestinationAddress();

            String sourceIpAddress = IPv4.fromIPv4Address(sourceAddress);
            String destinationIpAddress = IPv4.fromIPv4Address(destinationAddress);

            // #1 Kích thước gói tin
            int packetSize = ipv4Payload.getTotalLength();

            // #2 Thời gian đến của gói tin
            double epochSeconds = DateTimeUtil.getEpochSecond();

            String body = new String(ipv4Payload.serialize(), StandardCharsets.UTF_8);

            int tcpSrcPort = 0;
            int tcpDstPort = 0;
            int udpSrcPort = 0;
            int udpDstPort = 0;

            // Kiểm tra giao thức Transport (TCP hoặc UDP)
            byte protocol = ipv4Payload.getProtocol();
            if (protocol == IPv4.PROTOCOL_ICMP) {
                ICMP payload = (ICMP) ipv4Payload.getPayload();
            } else if (protocol == IPv4.PROTOCOL_TCP) {
                // Phân tích header TCP
                TCP payload = (TCP) ipv4Payload.getPayload();

                // Kiểm tra cổng nguồn và cổng đích
                tcpSrcPort = payload.getSourcePort();
                tcpDstPort = payload.getDestinationPort();
                //body = new String(payload.serialize(), StandardCharsets.UTF_8);
            } else if (protocol == IPv4.PROTOCOL_UDP) {
                UDP payload = (UDP) ipv4Payload.getPayload();

                // Kiểm tra cổng nguồn và cổng đích
                udpSrcPort = payload.getSourcePort();
                udpDstPort = payload.getDestinationPort();
            }

            log.info("timestamp {}, deviceId {}, portNumber {}: Received IPV4 packet from {} to {}" +
                            " with packetSize {}, epochSeconds = {}, flag = {}, protocol = {}, body = {}",
                    timestamp, deviceId, portNumber, sourceIpAddress, destinationIpAddress,
                    packetSize, epochSeconds, ipv4Payload.getFlags(), protocol, body.length());

            var data = new DataFlowDto(timestamp, tcpSrcPort, tcpDstPort, udpSrcPort, udpDstPort,
                    packetSize, protocol);
            apiClient.sendData(data);
        }
    }
}
