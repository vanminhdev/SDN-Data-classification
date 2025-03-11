package vn.edu.huce.dataclassification.rest;

import java.util.HashMap;
import java.util.Map;

import javax.ws.rs.BeanParam;
import javax.ws.rs.Consumes;
import javax.ws.rs.FormParam;
import javax.ws.rs.GET;
import javax.ws.rs.POST;
import javax.ws.rs.Path;
import javax.ws.rs.Produces;
import javax.ws.rs.core.MediaType;
import javax.ws.rs.core.Response;

import com.fasterxml.jackson.core.JsonProcessingException;

import io.atomix.primitive.operation.Operation;
import vn.edu.huce.dataclassification.ApplyFlowRule;
import vn.edu.huce.dataclassification.dtos.flowRule.CreateFlowRuleDto;
import vn.edu.huce.dataclassification.utils.ServiceType;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@Path("flowruleupdate")
public class FlowRuleUpdateResource extends BaseWebResource {
    private final Logger log = LoggerFactory.getLogger(getClass());

    @GET
    @Path("status")
    @Produces(MediaType.APPLICATION_JSON)
    public Response getStatus() {
        Map<String, String> status = new HashMap<>();
        status.put("status", "running");
        status.put("message", "My REST API is active!");
        return okResponse(status);
    }

    /**
     * Cập nhật flow rule
     * @param data
     * @return
     */
    @POST
    @Path("update")
    @Consumes(MediaType.APPLICATION_JSON)
    @Produces(MediaType.APPLICATION_JSON)
    public Response update(String data) {
        var applyFlowRuleService = get(ApplyFlowRule.class);
        CreateFlowRuleDto input;
        
        try {
            log.info("Received data: {}", data);
            input = this.mapper().readValue(data, CreateFlowRuleDto.class);
            log.info("Parsed input: {}", input);
            
            // Kiểm tra xem serviceType có hợp lệ không (nếu được cung cấp)
            if (input.getServiceType() != null && !input.getServiceType().isEmpty()) {
                try {
                    ServiceType serviceType = ServiceType.valueOf(input.getServiceType().toUpperCase());
                    log.info("Valid service type detected: {}", serviceType);
                } catch (IllegalArgumentException e) {
                    log.warn("Invalid service type: {}. Will use default meter.", input.getServiceType());
                }
            }
            
            // Áp dụng flow rule
            applyFlowRuleService.apply(input);
            
            return okResponse();
        } catch (JsonProcessingException e) {
            log.error("Error parsing JSON: {}", e.getMessage());
            return badRequestResponse(e.getMessage());
        }
    }
}
