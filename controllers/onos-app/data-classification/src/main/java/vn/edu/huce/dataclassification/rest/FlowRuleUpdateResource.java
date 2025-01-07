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
import vn.edu.huce.dataclassification.dtos.flowRule.FlowRuleDto;

@Path("flowruleupdate")
public class FlowRuleUpdateResource extends BaseWebResource {

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
        FlowRuleDto input;
        try {
            input = this.mapper().readValue(data, FlowRuleDto.class);
        } catch (JsonProcessingException e) {
            return badRequestResponse(e.getMessage());
        }
        // FlowRuleDto input = new FlowRuleDto(deviceId, ipSrc, ipDst,
        //         0, 0, 0, 0);
        applyFlowRuleService.apply(input);
        return okResponse();
    }
}
