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
import vn.edu.huce.dataclassification.utils.ApiClient;

public class MyPacketProcessor implements PacketProcessor {
    private final Logger log = LoggerFactory.getLogger(getClass());
    private ApiClient apiClient = new ApiClient();

    public static final short FIN = 0b0000000000000001;
    public static final short SYN = 0b0000000000000010;
    public static final short RST = 0b0000000000000100;
    public static final short PSH = 0b0000000000001000;
    public static final short ACK = 0b0000000000010000;
    public static final short URG = 0b0000000000100000;
    public static final short ECE = 0b0000000001000000;
    public static final short CWR = 0b0000000010000000;

    public static final int MIN_BYTE_ARR_LENTH = 100;

    private String byteToHex(byte num) {
        char[] hexDigits = new char[2];
        hexDigits[0] = Character.forDigit((num >> 4) & 0xF, 16);
        hexDigits[1] = Character.forDigit((num & 0xF), 16);
        return new String(hexDigits);
    }

    private String encodeHexString(byte[] byteArray) {
        StringBuilder hexStringBuffer = new StringBuilder();
        for (byte b : byteArray) {
            hexStringBuffer.append(byteToHex(b));
        }
        return hexStringBuffer.toString();
    }

    @Override
    public void process(PacketContext context) {
        // Xử lý gói tin ở đây
        // var parsed = context.inPacket().parsed();
        InboundPacket pkt = context.inPacket();
        Ethernet ethPacket = pkt.parsed();
        short etherType = ethPacket.getEtherType();
        short flags = 0;

        if (etherType == Ethernet.TYPE_LLDP) {
            ConnectPoint receivedFrom = pkt.receivedFrom();
            DeviceId deviceId = receivedFrom.deviceId();
            PortNumber portNumber = receivedFrom.port();
            MacAddress sourceMac = ethPacket.getSourceMAC(); // địa chỉ mac source
            MacAddress destMac = ethPacket.getDestinationMAC(); // địa chỉ mac dest
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
            String dataStr = "";
            if (protocol == IPv4.PROTOCOL_ICMP) {
                ICMP payload = (ICMP) ipv4Payload.getPayload();
            } else if (protocol == IPv4.PROTOCOL_TCP) {
                // Phân tích header TCP
                TCP payload = (TCP) ipv4Payload.getPayload();
                byte[] data = payload.serialize();

                // Kiểm tra cổng nguồn và cổng đích
                int srcPort = payload.getSourcePort();
                int dstPort = payload.getDestinationPort();

                dataStr = encodeHexString(data);
                handleData(sourceIpAddress, srcPort, destinationIpAddress, dstPort, data);

                /*
                 * payload.getOptions();
                 * payload.getChecksum();
                 * 
                 * flags = payload.getFlags();
                 * 
                 * if ((flags & FIN) == FIN) {
                 * System.out.println("FIN flag is set");
                 * }
                 * if ((flags & SYN) == SYN) {
                 * System.out.println("SYN flag is set");
                 * }
                 * if ((flags & RST) == RST) {
                 * System.out.println("RST flag is set");
                 * }
                 * if ((flags & PSH) == PSH) {
                 * System.out.println("PSH flag is set");
                 * }
                 * if ((flags & ACK) == ACK) {
                 * System.out.println("ACK flag is set");
                 * }
                 * if ((flags & URG) != URG) {
                 * System.out.println("URG flag is set");
                 * }
                 * if ((flags & ECE) == ECE) {
                 * System.out.println("ECE flag is set");
                 * }
                 * if ((flags & CWR) == CWR) {
                 * System.out.println("CWR flag is set");
                 * }
                 */

            } else if (protocol == IPv4.PROTOCOL_UDP) {
                UDP payload = (UDP) ipv4Payload.getPayload();
                byte[] data = payload.serialize();

                // Kiểm tra cổng nguồn và cổng đích
                int srcPort = payload.getSourcePort();
                int dstPort = payload.getDestinationPort();

                dataStr = encodeHexString(data);
                handleData(sourceIpAddress, srcPort, destinationIpAddress, dstPort, data);
            }
            log.info("Received IPV4 packet from {} to {} with protocol {}, data = {}, flag = {}",
                    sourceIpAddress, destinationIpAddress, protocol, dataStr, flags);
        }
    }

    private void handleData(String sourceIpAddress, int srcPort, String destinationIpAddress, int dstPort,
            byte[] data) {
        if (data.length < MIN_BYTE_ARR_LENTH) {
            return;
        }
        String dataStr = encodeHexString(data);
        apiClient.sendData(sourceIpAddress, srcPort, destinationIpAddress, dstPort, dataStr);
    }
}
