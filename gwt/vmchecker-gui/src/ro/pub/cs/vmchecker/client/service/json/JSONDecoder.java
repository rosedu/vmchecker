package ro.pub.cs.vmchecker.client.service.json;

import com.google.gwt.json.client.JSONException;

public interface JSONDecoder<T> {

	T decode(String text) throws JSONException; 
}
