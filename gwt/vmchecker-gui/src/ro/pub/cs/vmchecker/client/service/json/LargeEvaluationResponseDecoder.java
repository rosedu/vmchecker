package ro.pub.cs.vmchecker.client.service.json;

import ro.pub.cs.vmchecker.client.model.LargeEvaluationResponse;

import com.google.gwt.json.client.JSONObject;
import com.google.gwt.json.client.JSONParser;
import com.google.gwt.json.client.JSONValue;

public final class LargeEvaluationResponseDecoder extends JSONDecoder<LargeEvaluationResponse> {

	private static final String statusKey = "status";
	private static final String errorKey = "error";

	@Override
	protected LargeEvaluationResponse decode(String text) {
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
