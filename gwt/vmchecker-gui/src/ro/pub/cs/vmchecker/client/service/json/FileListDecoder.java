package ro.pub.cs.vmchecker.client.service.json;

import com.google.gwt.json.client.JSONObject;
import com.google.gwt.json.client.JSONParser;
import com.google.gwt.json.client.JSONValue;
import com.google.gwt.json.client.JSONArray;


import ro.pub.cs.vmchecker.client.model.FileList;

public final class FileListDecoder extends JSONDecoder<FileList> {

	private static final String filenameKey = "fileName";

	@Override
	protected FileList decode(String text) {

		JSONValue jsonValue = JSONParser.parse(text);
		JSONArray jsonArray = jsonValue.isArray();

		if(jsonArray.size() == 0) return new FileList(null);

		String[] results = new String[jsonArray.size()];
		for (int i = 0; i < jsonArray.size(); i++) {
			JSONObject jsonObj = jsonArray.get(i).isObject();
			results[i] = jsonObj.get(filenameKey).isString().stringValue();
		}
		return new FileList(results);
	}

}
