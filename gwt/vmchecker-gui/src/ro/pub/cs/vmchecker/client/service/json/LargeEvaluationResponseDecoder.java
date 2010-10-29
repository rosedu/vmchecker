package ro.pub.cs.vmchecker.client.service.json;

import ro.pub.cs.vmchecker.client.model.LargeEvaluationResponse;

import com.google.gwt.json.client.JSONObject;
import com.google.gwt.json.client.JSONParser;
import com.google.gwt.json.client.JSONValue;

public class LargeEvaluationResponseDecoder implements JSONDecoder<LargeEvaluationResponse> {

	public static final String statusKey = "status";
	public static final String errorKey = "error";

	@Override
	public LargeEvaluationResponse decode(String text) throws Exception {
		JSONValue jsonValue = JSONParser.parse(text);
		JSONObject jsonObj = jsonValue.isObject();

		boolean status = jsonObj.get(statusKey).isBoolean().booleanValue();
		if(!status) {
			String error = jsonObj.get(errorKey).isString().stringValue();
			return new LargeEvaluationResponse(status, error);
		} else
			return new LargeEvaluationResponse(status, "");
	}

}
