package ro.pub.cs.vmchecker.client.service.json;

import com.google.gwt.json.client.JSONArray;
import com.google.gwt.json.client.JSONObject;
import com.google.gwt.json.client.JSONParser;
import com.google.gwt.json.client.JSONValue;

import ro.pub.cs.vmchecker.client.model.Assignment;

public final class AssignmentsListDecoder extends JSONDecoder<Assignment[]> {

	private static final String idKey = "assignmentId";
	private static final String titleKey = "assignmentTitle";
	private static final String storageTypeKey = "assignmentStorage";
	private static final String storageHostKey = "assignmentStorageHost";
	private static final String storageBasepathKey = "assignmentStorageBasepath";
	private static final String deadlineKey = "deadline";
	private static final String statementLinkKey = "statementLink";
	private static final String teamKey = "team";

	@Override
	protected Assignment[] decode(String text) {
		JSONValue jsonValue = JSONParser.parse(text);
		JSONArray jsonArray = jsonValue.isArray();
		Assignment[] assignments = null;

		assignments = new Assignment[jsonArray.size()];
		for (int i = 0; i < jsonArray.size(); i++) {
			assignments[i] = parseAssignment(jsonArray.get(i).isObject());
		}
		return assignments;
	}

	private Assignment parseAssignment(JSONObject jsonObj) {
		String id = jsonObj.get(idKey).isString().stringValue();
		String title = jsonObj.get(titleKey).isString().stringValue();
		Assignment.StorageType storageType =
			Assignment.StorageType.valueOf(jsonObj.get(storageTypeKey).isString().stringValue().toUpperCase());
		String deadline = jsonObj.get(deadlineKey).isString().stringValue();
		String statementLink = jsonObj.get(statementLinkKey).isString().stringValue();
		boolean hasTeam = jsonObj.keySet().contains(teamKey);
		String team = null;
		if (hasTeam) {
			team = jsonObj.get(teamKey).isString().stringValue();
		}
		if (storageType == Assignment.StorageType.NORMAL) {
			return new Assignment(id, title, storageType, null, null, deadline, statementLink, hasTeam, team);
		} else {
			String storageHost = jsonObj.get(storageHostKey).isString().stringValue();
			String storageBasepath = jsonObj.get(storageBasepathKey).isString().stringValue();
			return new Assignment(id, title, storageType, storageHost, storageBasepath, deadline, statementLink, hasTeam, team);
		}
	}

}
