package ro.pub.cs.vmchecker.client.service.json;

import com.google.gwt.json.client.JSONObject;
import com.google.gwt.json.client.JSONParser;
import com.google.gwt.json.client.JSONValue;

import ro.pub.cs.vmchecker.client.model.UploadStatus;

public class UploadResponseDecoder implements JSONDecoder<UploadStatus> {

	public static final String statusKey = "status";
	public static final String dumpLogKey = "dumpLog"; 
	
	@Override
	public UploadStatus decode(String text) throws Exception {
		JSONValue jsonValue = JSONParser.parse(text);
		JSONObject jsonObject = jsonValue.isObject();
		boolean status = jsonObject.get(statusKey).isBoolean().booleanValue();
		String dumpLog = jsonObject.get(dumpLogKey).isString().stringValue();
		return new UploadStatus(status, dumpLog);
	}

}
