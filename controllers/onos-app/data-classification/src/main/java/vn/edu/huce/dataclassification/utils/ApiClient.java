package vn.edu.huce.dataclassification.utils;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.mashape.unirest.http.HttpResponse;
import com.mashape.unirest.http.Unirest;
import com.mashape.unirest.http.exceptions.UnirestException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

public class ApiClient {
    private static final String BASE_URL = "http://192.168.0.4:5000";

    private final Logger log = LoggerFactory.getLogger(getClass());

    public void sendData(String srcIp, int srcPort, String destIp, int destPort, String hexData) {
        try {
            // Dữ liệu JSON
            Map<String, Object> data = new HashMap<>();
            data.put("src_ip", srcIp);
            data.put("dest_ip", destIp);
            data.put("src_port", srcPort);
            data.put("dest_port", destPort);
            data.put("hex_data", hexData);

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