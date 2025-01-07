package vn.edu.huce.dataclassification.rest;

import javax.ws.rs.core.Response;

import org.json.JSONObject;
import org.onosproject.rest.AbstractWebResource;

import com.fasterxml.jackson.core.JsonProcessingException;

public class BaseWebResource extends AbstractWebResource {

    protected Response ok(JSONObject jsonObject) {
        return Response.ok(jsonObject.toString()).build();
    }

    protected Response  okResponse(Object object) {
        String jsonResponse = null;
        try {
            jsonResponse = this.mapper().writeValueAsString(object);
        } catch (JsonProcessingException e) {
            Response.status(500, e.getMessage());
        }
        return Response.ok(jsonResponse).build();
    }

    protected Response okResponse() {
        return Response.ok().build();
    }

    protected Response badRequestResponse(String string) {
        return Response.status(400, string).build();
    }
}
