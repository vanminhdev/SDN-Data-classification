package vn.edu.huce.dataclassification.utils;

import com.fasterxml.jackson.databind.ObjectMapper;
import shaded.org.apache.http.client.methods.CloseableHttpResponse;
import shaded.org.apache.http.client.methods.HttpPost;
import shaded.org.apache.http.entity.StringEntity;
import shaded.org.apache.http.impl.client.CloseableHttpClient;
import shaded.org.apache.http.impl.client.HttpClients;
import shaded.org.apache.http.util.EntityUtils;

import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class ApiClient {
    private static final String BASE_URL = "http://192.168.0.4:5000";

    private final Logger log = LoggerFactory.getLogger(getClass());

    public void sendData(String srcIp, int srcPort, String destIp, int destPort, String hexData) {
        CloseableHttpClient httpClient = null;
        try {
            // Tạo HTTP client
            httpClient = HttpClients.createDefault();
            // Tạo HTTP POST request
            HttpPost httpPost = new HttpPost(BASE_URL + "/api/push-data");

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

            // Thêm dữ liệu JSON vào request
            StringEntity entity = new StringEntity(json);
            httpPost.setEntity(entity);
            httpPost.setHeader("Content-Type", "application/json");

            // Gửi request và lấy response
            try (CloseableHttpResponse response = httpClient.execute(httpPost)) {
                log.info("call api send data: response = {}", EntityUtils.toString(response.getEntity()));
            }
        } catch (IOException e) {
            log.error("call api send data: {}", e.getMessage());
        } finally {
            if (httpClient != null) {
                try {
                    httpClient.close();
                } catch (IOException e) {
                    log.error("close http client: {}", e.getMessage());
                }
            }
        }
    }
}
