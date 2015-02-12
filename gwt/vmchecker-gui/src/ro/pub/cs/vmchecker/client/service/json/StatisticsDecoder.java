package ro.pub.cs.vmchecker.client.service.json;

import java.util.HashMap;

import com.google.gwt.json.client.JSONArray;
import com.google.gwt.json.client.JSONObject;
import com.google.gwt.json.client.JSONParser;
import com.google.gwt.json.client.JSONValue;

import ro.pub.cs.vmchecker.client.model.ResultInfo;

public final class StatisticsDecoder extends JSONDecoder<ResultInfo[]> {

	private static final String ownerKey = "gradeOwner";
	private static final String nameKey = "name";
	private static final String resultsKey = "results";

	@Override
	protected ResultInfo[] decode(String text) {
		JSONValue jsonValue = JSONParser.parse(text); 
		JSONArray jsonArray = jsonValue.isArray();
		ResultInfo[] results = new ResultInfo[jsonArray.size()];
		for (int i = 0; i < jsonArray.size(); i++) {
			JSONObject studentObj = jsonArray.get(i).isObject();
			String owner = studentObj.get(ownerKey).isString().stringValue();
			String name = studentObj.get(nameKey).isString().stringValue();
			HashMap<String, String> assignmentsResults = new HashMap<String, String>();
			JSONObject resultsObj = studentObj.get(resultsKey).isObject();
			for (String assignmentId : resultsObj.keySet()) {
				assignmentsResults.put(assignmentId, resultsObj.get(assignmentId).isString().stringValue());
			}
			results[i] = new ResultInfo(ResultInfo.OwnerType.valueOf(owner.toUpperCase()), name, assignmentsResults);
		}

		return results;
	}

}
