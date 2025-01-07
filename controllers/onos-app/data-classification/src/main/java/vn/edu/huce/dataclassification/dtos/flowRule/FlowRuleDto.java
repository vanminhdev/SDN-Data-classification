package vn.edu.huce.dataclassification.dtos.flowRule;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonProperty;

public class FlowRuleDto {
    private String deviceId;
    private String ipSrc;
    private String ipDst;
    private int tcpPortSrc;
    private int tcpPortDst;
    private int udpPortSrc;
    private int udpPortDst;

    public FlowRuleDto() {
    }

    @JsonCreator
    public FlowRuleDto(
        @JsonProperty("deviceId") String deviceId,
        @JsonProperty("ipSrc") String ipSrc,
        @JsonProperty("ipDst") String ipDst,
        @JsonProperty("tcpPortSrc") int tcpPortSrc,
        @JsonProperty("tcpPortDst") int tcpPortDst,
        @JsonProperty("udpPortSrc") int udpPortSrc,
        @JsonProperty("udpPortDst") int udpPortDst
    ) {
        this.deviceId = deviceId;
        this.ipSrc = ipSrc;
        this.ipDst = ipDst;
        this.tcpPortSrc = tcpPortSrc;
        this.tcpPortDst = tcpPortDst;
        this.udpPortSrc = udpPortSrc;
        this.udpPortDst = udpPortDst;
    }

    @Override
    public String toString() {
        return "FlowRuleDto [deviceId=" + deviceId + ", ipSrc=" + ipSrc + ", ipDst=" + ipDst + ", tcpPortSrc="
                + tcpPortSrc + ", tcpPortDst=" + tcpPortDst + ", udpPortSrc=" + udpPortSrc + ", udpPortDst="
                + udpPortDst + "]";
    }

    public String getDeviceId() {
        return deviceId;
    }

    public void setDeviceId(String deviceId) {
        this.deviceId = deviceId;
    }

    public String getIpSrc() {
        if (ipSrc == null) {
            return null;
        }
        return ipSrc.trim();
    }

    public void setIpSrc(String ipSrc) {
        this.ipSrc = ipSrc;
    }

    public String getIpDst() {
        if (ipDst == null) {
            return null;
        }
        return ipDst.trim();
    }

    public void setIpDst(String ipDst) {
        this.ipDst = ipDst;
    }

    public int getTcpPortSrc() {
        return tcpPortSrc;
    }

    public void setTcpPortSrc(int tcpPortSrc) {
        if (tcpPortSrc < 0) {
            tcpPortSrc = 0;
        }
        this.tcpPortSrc = tcpPortSrc;
    }

    public int getTcpPortDst() {
        return tcpPortDst;
    }

    public void setTcpPortDst(int tcpPortDst) {
        if (tcpPortDst < 0) {
            tcpPortDst = 0;
        }
        this.tcpPortDst = tcpPortDst;
    }

    public int getUdpPortSrc() {
        return udpPortSrc;
    }

    public void setUdpPortSrc(int udpPortSrc) {
        if (udpPortSrc < 0) {
            udpPortSrc = 0;
        }
        this.udpPortSrc = udpPortSrc;
    }

    public int getUdpPortDst() {
        return udpPortDst;
    }

    public void setUdpPortDst(int udpPortDst) {
        if (udpPortDst < 0) {
            udpPortDst = 0;
        }
        this.udpPortDst = udpPortDst;
    }
}
