package ro.pub.cs.vmchecker.client.service.json;

import ro.pub.cs.vmchecker.client.model.AuthenticationResponse;
import ro.pub.cs.vmchecker.client.model.User;

import com.google.gwt.json.client.JSONObject;
import com.google.gwt.json.client.JSONParser;
import com.google.gwt.json.client.JSONValue;

public class AuthenticationResponseDecoder implements JSONDecoder<AuthenticationResponse> {

	public static final String statusKey = "status"; 
	public static final String usernameKey = "username"; 
	public static final String useridKey = "userid";
	public static final String infoKey = "info"; 
	
	@Override
	public AuthenticationResponse decode(String text) throws Exception {
		JSONValue jsonValue = JSONParser.parse(text);
		JSONObject jsonObj = jsonValue.isObject();

		boolean status = jsonObj.get(statusKey).isBoolean().booleanValue();
		String username = jsonObj.get(usernameKey).isString().stringValue();
		String userid = jsonObj.get(useridKey).isString().stringValue();
		String info = jsonObj.get(infoKey).isString().stringValue();
		return new AuthenticationResponse(status, new User(userid, username), info);
	}

}
