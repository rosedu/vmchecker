package ro.pub.cs.vmchecker.client.service.json;

import ro.pub.cs.vmchecker.client.model.Result;

import com.google.gwt.json.client.JSONObject;
import com.google.gwt.json.client.JSONParser;
import com.google.gwt.json.client.JSONValue;

public class ResultDecoder implements JSONDecoder<Result> {

	public static final String logKey = "resultLog"; 
	
	@Override
	public Result decode(String text) throws Exception {
		try {
			JSONValue jsonValue = JSONParser.parse(text); 
			JSONObject jsonObj = jsonValue.isObject();
			return new Result(jsonObj.get(logKey).isString().stringValue()); 
		} catch (Exception e) {
			throw e; 
		}
	}

}
