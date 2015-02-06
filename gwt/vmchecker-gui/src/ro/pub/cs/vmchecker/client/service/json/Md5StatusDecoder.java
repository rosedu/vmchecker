package ro.pub.cs.vmchecker.client.service.json;

import com.google.gwt.json.client.JSONObject;
import com.google.gwt.json.client.JSONParser;
import com.google.gwt.json.client.JSONValue;

import ro.pub.cs.vmchecker.client.model.Md5Status;

public final class Md5StatusDecoder extends JSONDecoder<Md5Status> {

	private static final String fileExistsKey = "fileExists";
	private static final String md5SumKey = "md5Sum";
	private static final String uploadTimeKey = "uploadTime";

	@Override
	protected Md5Status decode(String text) {
		JSONValue jsonValue = JSONParser.parse(text);
		JSONObject jsonObject = jsonValue.isObject();
		boolean fileExists = jsonObject.get(fileExistsKey).isBoolean().booleanValue();
		if(fileExists) {
			String md5Sum = jsonObject.get(md5SumKey).isString().stringValue();
			String uploadTime = jsonObject.get(uploadTimeKey).isString().stringValue();
			return new Md5Status(fileExists, md5Sum, uploadTime);
		} else
		    return new Md5Status(fileExists, "", "");
	}

}
