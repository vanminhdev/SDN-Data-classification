package vn.edu.huce.dataclassification.utils;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.mashape.unirest.http.HttpResponse;
import com.mashape.unirest.http.Unirest;
import com.mashape.unirest.http.exceptions.UnirestException;

import org.onlab.packet.IPv4;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import vn.edu.huce.dataclassification.dtos.data.DataFlowDto;

import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

public class ApiClient {
    private static final String BASE_URL = "http://192.168.0.4:5000";

    private final Logger log = LoggerFactory.getLogger(getClass());

    public void sendData(DataFlowDto input) {
        try {
            // Dữ liệu JSON
            Map<String, Object> data = new HashMap<>();
            data.put("time_epoch", input.getTimeEpoch());
            data.put("ip_proto", input.getIpProto());
            if (input.getIpProto() == IPv4.PROTOCOL_TCP) {
                data.put("src_port", input.getTcpSrcPort());
                data.put("dst_port", input.getTcpDstPort());
            } else if (input.getIpProto() == IPv4.PROTOCOL_UDP) {
                data.put("src_port", input.getUdpSrcPort());
                data.put("dst_port", input.getUdpDstPort());
            }
            data.put("frame_len", input.getFrameLen());
            data.put("device_id", input.getDeviceId());
            data.put("src_ip", input.getSrcIp());
            data.put("dst_ip", input.getDstIp());

            // Chuyển đổi map thành JSON
            ObjectMapper objectMapper = new ObjectMapper();
            String json = objectMapper.writeValueAsString(data);

            // Gửi request và lấy response
            HttpResponse<String> response = Unirest.post(BASE_URL + "/api/push-data")
                    .header("Content-Type", "application/json")
                    .body(json)
                    .asString();
            log.info("call api send data: response = {}", response.getBody());
        } catch (UnirestException | IOException e) {
            log.error("call api send data: {}", e.getMessage());
        }
    }
}