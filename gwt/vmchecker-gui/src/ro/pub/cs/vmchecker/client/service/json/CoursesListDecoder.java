package ro.pub.cs.vmchecker.client.service.json;

import com.google.gwt.core.client.GWT;
import com.google.gwt.json.client.JSONArray;
import com.google.gwt.json.client.JSONException;
import com.google.gwt.json.client.JSONObject;
import com.google.gwt.json.client.JSONParser;
import com.google.gwt.json.client.JSONValue;

import ro.pub.cs.vmchecker.client.model.Course;

public class CoursesListDecoder implements JSONDecoder<Course[]> {

	public static final String idKey = "id";
	public static final String titleKey = "title"; 
	
	@Override
	public Course[] decode(String text) {
		// TODO Auto-generated method stub
		GWT.log("Decoding: " + text, null); 
		try {
			JSONValue jsonValue = JSONParser.parse(text);
		    JSONArray jsonArray;
		     
		    if ((jsonArray = jsonValue.isArray()) != null) {
		    	Course[] courses = new Course[jsonArray.size()]; 
		    	for (int i = 0; i < jsonArray.size(); i++) {
		    		Course course = parseCourse(jsonArray.get(i).isObject());
		    		courses[i] = course; 
		    	}
		    	return courses; 
		    } 
		} catch (JSONException e) {
			throw e; 
		}
		return null; 
	}
	
	private Course parseCourse(JSONObject jsonObj) {
		if (jsonObj == null)
			return null; 
		String id = jsonObj.get(idKey).isString().stringValue(); 
		String title = jsonObj.get(titleKey).isString().stringValue(); 
		return new Course(id, title); 
	}
}
