package vn.edu.huce.dataclassification.rest;

import java.util.HashMap;
import java.util.Map;

import javax.ws.rs.Consumes;
import javax.ws.rs.GET;
import javax.ws.rs.POST;
import javax.ws.rs.Path;
import javax.ws.rs.Produces;
import javax.ws.rs.core.MediaType;
import javax.ws.rs.core.Response;

import org.json.JSONObject;

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

    // @POST
    // @Path("update")
    // @Consumes(MediaType.APPLICATION_JSON)
    // public Response update(String deviceId, String ipSrc, String ipDst) {
    //     var applyFlowRuleService = get(ApplyFlowRule.class);
    //     FlowRuleDto input = new FlowRuleDto(deviceId, ipSrc, ipDst,
    //             0, 0, 0, 0);
    //     applyFlowRuleService.apply(input);
    //     return okResponse();
    // }
}
