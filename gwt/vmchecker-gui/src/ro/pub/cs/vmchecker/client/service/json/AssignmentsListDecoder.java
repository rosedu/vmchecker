package ro.pub.cs.vmchecker.client.service.json;

import com.google.gwt.json.client.JSONArray;
import com.google.gwt.json.client.JSONObject;
import com.google.gwt.json.client.JSONParser;
import com.google.gwt.json.client.JSONValue;

import ro.pub.cs.vmchecker.client.model.Assignment;

public class AssignmentsListDecoder implements JSONDecoder<Assignment[]> {

	public static final String idKey = "assignmentId"; 
	public static final String titleKey = "assignmentTitle"; 
	public static final String deadlineKey = "deadline"; 
	
	@Override
	public Assignment[] decode(String text) throws Exception {
		JSONValue jsonValue = JSONParser.parse(text); 
		JSONArray jsonArray; 
		Assignment[] assignments = null; 
		
		if ((jsonArray = jsonValue.isArray()) != null) {
			assignments = new Assignment[jsonArray.size()]; 
			for (int i = 0; i < jsonArray.size(); i++) {
				assignments[i] = parseAssignment(jsonArray.get(i).isObject()); 
			}
		}
		return assignments;
	}

	private Assignment parseAssignment(JSONObject jsonObj) {
		if (jsonObj == null) 
			return null; 
		String id = jsonObj.get(idKey).isString().stringValue(); 
		String title = jsonObj.get(titleKey).isString().stringValue();
		String deadline = jsonObj.get(deadlineKey).isString().stringValue();
		return new Assignment(id, title, deadline); 
	}
	
}
