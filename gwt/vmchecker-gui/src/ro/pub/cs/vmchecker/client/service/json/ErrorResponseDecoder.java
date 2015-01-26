package ro.pub.cs.vmchecker.client.service.json;

import com.google.gwt.json.client.JSONObject;
import com.google.gwt.json.client.JSONParser;
import com.google.gwt.json.client.JSONValue;

import ro.pub.cs.vmchecker.client.model.ErrorResponse;

public final class ErrorResponseDecoder extends JSONDecoder<ErrorResponse> {

	private static final String errorTypeKey = "errorType";
	private static final String errorMessageKey = "errorMessage"; 
	private static final String errorTraceKey = "errorTrace";
	
	@Override
	protected ErrorResponse decode(String text) {
		JSONValue jsonValue = JSONParser.parse(text);
		JSONObject jsonObj = jsonValue.isObject();

		int typeCode = (int) jsonObj.get(errorTypeKey).isNumber().doubleValue();
		String message = jsonObj.get(errorMessageKey).isString().stringValue();
		String trace = jsonObj.get(errorTraceKey).isString().stringValue();
		return new ErrorResponse(typeCode, message, trace);
	}

}
