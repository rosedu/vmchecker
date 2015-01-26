package ro.pub.cs.vmchecker.client.service.json;

import java.util.HashMap;

import com.google.gwt.json.client.JSONArray;
import com.google.gwt.json.client.JSONObject;
import com.google.gwt.json.client.JSONParser;
import com.google.gwt.json.client.JSONValue;

import ro.pub.cs.vmchecker.client.model.StudentInfo;

public final class StatisticsDecoder extends JSONDecoder<StudentInfo[]> {

	private static final String nameKey = "studentName";
	private static final String idKey = "studentId";
	private static final String resultsKey = "results";
	
	@Override
	protected StudentInfo[] decode(String text) {
		JSONValue jsonValue = JSONParser.parse(text); 
		JSONArray jsonArray = jsonValue.isArray(); 
		StudentInfo[] result = new StudentInfo[jsonArray.size()];
		for (int i = 0; i < jsonArray.size(); i++) {
			JSONObject studentObj = jsonArray.get(i).isObject();
			String name = studentObj.get(nameKey).isString().stringValue();
			String id = studentObj.get(idKey).isString().stringValue();
			HashMap<String, String> assignmentsResults = new HashMap<String, String>(); 
			JSONObject resultsObj = studentObj.get(resultsKey).isObject(); 
			for (String assignmentId : resultsObj.keySet()) {
				assignmentsResults.put(assignmentId, resultsObj.get(assignmentId).isString().stringValue()); 
			}
			result[i] = new StudentInfo(name, id, assignmentsResults); 
		}
		
		return result; 
	}

}
