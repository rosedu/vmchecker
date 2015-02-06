package ro.pub.cs.vmchecker.client.service.json;

import com.google.gwt.core.client.JavaScriptException;
import com.google.gwt.core.client.GWT;

public abstract class JSONDecoder<T> {

	private boolean failed = false;
	private T result = null;

	protected abstract T decode(String text);

	public void parse(String text) {
		try {
			result = decode(text);
			failed = false;
		} catch (JavaScriptException | NullPointerException e) {
			failed = true;
			GWT.log("[JSONDecoder.parse()]", e);
		}
	}

	public boolean errorsEncountered() {
		return failed;
	}

	public T getResult() {
		return result;
	}

}
