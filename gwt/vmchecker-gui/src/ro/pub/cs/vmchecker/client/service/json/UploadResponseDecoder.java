package ro.pub.cs.vmchecker.client.service.json;

import com.google.gwt.json.client.JSONObject;
import com.google.gwt.json.client.JSONParser;
import com.google.gwt.json.client.JSONValue;

import ro.pub.cs.vmchecker.client.model.UploadStatus;

public final class UploadResponseDecoder extends JSONDecoder<UploadStatus> {

	private static final String statusKey = "status";
	private static final String dumpLogKey = "dumpLog";
	
	@Override
	protected UploadStatus decode(String text) {
		JSONValue jsonValue = JSONParser.parse(text);
		JSONObject jsonObject = jsonValue.isObject();
		boolean status = jsonObject.get(statusKey).isBoolean().booleanValue();
		String dumpLog = jsonObject.get(dumpLogKey).isString().stringValue();
		return new UploadStatus(status, dumpLog);
	}

}
