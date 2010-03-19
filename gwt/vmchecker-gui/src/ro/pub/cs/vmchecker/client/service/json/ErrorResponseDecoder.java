package ro.pub.cs.vmchecker.client.service.json;

import com.google.gwt.core.client.GWT;
import com.google.gwt.json.client.JSONObject;
import com.google.gwt.json.client.JSONParser;
import com.google.gwt.json.client.JSONValue;

import ro.pub.cs.vmchecker.client.model.ErrorResponse;

public class ErrorResponseDecoder implements JSONDecoder<ErrorResponse> {

	public static final String errorTypeKey = "errorType"; 
	public static final String errorMessageKey = "errorMessage"; 
	public static final String errorTraceKey = "errorTrace"; 
	
	@Override
	public ErrorResponse decode(String text) throws Exception {
		try {
			JSONValue jsonValue = JSONParser.parse(text);
			JSONObject jsonObj = jsonValue.isObject(); 
			
			int typeCode = (int)jsonObj.get(errorTypeKey).isNumber().doubleValue();
			String message = jsonObj.get(errorMessageKey).isString().stringValue();
			String trace = jsonObj.get(errorTraceKey).isString().stringValue(); 
			return new ErrorResponse(typeCode, message, trace); 
		} catch (Exception e) {
			GWT.log(e.toString(), null);  
			throw e;
		}
	}

}
