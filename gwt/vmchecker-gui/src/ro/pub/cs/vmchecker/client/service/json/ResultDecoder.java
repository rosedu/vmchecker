package ro.pub.cs.vmchecker.client.service.json;

import ro.pub.cs.vmchecker.client.model.EvaluationResult;

import com.google.gwt.json.client.JSONArray;
import com.google.gwt.json.client.JSONObject;
import com.google.gwt.json.client.JSONParser;
import com.google.gwt.json.client.JSONValue;

public class ResultDecoder implements JSONDecoder<EvaluationResult[]> {
	
	@Override
	public EvaluationResult[] decode(String text) throws Exception {
		JSONValue jsonValue = JSONParser.parse(text);
		JSONArray jsonArray = jsonValue.isArray(); 
		
		EvaluationResult[] results = new EvaluationResult[jsonArray.size()]; 
		for (int i = 0; i < jsonArray.size(); i++) {
			JSONObject jsonObj = jsonArray.get(i).isObject();
			for (String step : jsonObj.keySet()) {
				results[i] = new EvaluationResult(step, jsonObj.get(step).isString().stringValue()); 
				break; 
			}
		}
		return results; 
	}

}
