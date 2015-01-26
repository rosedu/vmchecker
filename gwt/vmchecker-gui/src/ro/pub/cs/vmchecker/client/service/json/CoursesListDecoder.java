package ro.pub.cs.vmchecker.client.service.json;

import com.google.gwt.json.client.JSONArray;
import com.google.gwt.json.client.JSONObject;
import com.google.gwt.json.client.JSONParser;
import com.google.gwt.json.client.JSONValue;

import ro.pub.cs.vmchecker.client.model.Course;

public final class CoursesListDecoder extends JSONDecoder<Course[]> {

	private static final String idKey = "id";
	private static final String titleKey = "title";
	
	@Override
	protected Course[] decode(String text) {
		JSONValue jsonValue = JSONParser.parse(text);
		JSONArray jsonArray = jsonValue.isArray();

		Course[] courses = new Course[jsonArray.size()];
		for (int i = 0; i < jsonArray.size(); i++) {
			courses[i] = parseCourse(jsonArray.get(i).isObject());
		}
		return courses;
	}
	
	private Course parseCourse(JSONObject jsonObj) {
		String id = jsonObj.get(idKey).isString().stringValue(); 
		String title = jsonObj.get(titleKey).isString().stringValue(); 
		return new Course(id, title); 
	}
}
