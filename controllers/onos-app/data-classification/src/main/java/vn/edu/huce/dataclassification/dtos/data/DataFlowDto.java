package vn.edu.huce.dataclassification.dtos.data;

/**
 * Dữ liệu thu thập
 */
public class DataFlowDto {
    private long timeEpoch;
    private int tcpSrcPort;
    private int tcpDstPort;
    private int udpSrcPort;
    private int udpDstPort;
    private long frameLen;
    private int ipProto;
    private String deviceId;

    public String getDeviceId() {
        return deviceId;
    }

    public void setDeviceId(String deviceId) {
        this.deviceId = deviceId;
    }

    public long getTimeEpoch() {
        return timeEpoch;
    }

    public void setTimeEpoch(long timeEpoch) {
        this.timeEpoch = timeEpoch;
    }

    public int getTcpSrcPort() {
        return tcpSrcPort;
    }

    public void setTcpSrcPort(int tcpSrcPort) {
        this.tcpSrcPort = tcpSrcPort;
    }

    public int getTcpDstPort() {
        return tcpDstPort;
    }

    public void setTcpDstPort(int tcpDstPort) {
        this.tcpDstPort = tcpDstPort;
    }

    public int getUdpSrcPort() {
        return udpSrcPort;
    }

    public void setUdpSrcPort(int udpSrcPort) {
        this.udpSrcPort = udpSrcPort;
    }

    public int getUdpDstPort() {
        return udpDstPort;
    }

    public void setUdpDstPort(int udpDstPort) {
        this.udpDstPort = udpDstPort;
    }

    public long getFrameLen() {
        return frameLen;
    }

    public void setFrameLen(long frameLen) {
        this.frameLen = frameLen;
    }

    public int getIpProto() {
        return ipProto;
    }

    public void setIpProto(int ipProto) {
        this.ipProto = ipProto;
    }

    public DataFlowDto() {
    }

    public DataFlowDto(long timeEpoch, int tcpSrcPort, int tcpDstPort,
                       int udpSrcPort, int udpDstPort, long frameLen, int ipProto, String deviceId) {
        this.timeEpoch = timeEpoch;
        this.tcpSrcPort = tcpSrcPort;
        this.tcpDstPort = tcpDstPort;
        this.udpSrcPort = udpSrcPort;
        this.udpDstPort = udpDstPort;
        this.frameLen = frameLen;
        this.ipProto = ipProto;
        this.deviceId = deviceId;
    }
}
