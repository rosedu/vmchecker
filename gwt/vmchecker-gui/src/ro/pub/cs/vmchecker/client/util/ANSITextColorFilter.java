package ro.pub.cs.vmchecker.client.util;

import java.util.Map;
import java.util.HashMap;
import java.util.Collections;

import com.google.gwt.core.client.GWT;

public class ANSITextColorFilter {
	private static final Map<String, String> codeColorMap;
 	static {
		Map<String, String> map = new HashMap<String, String>();
		map.put("30", "#000000");
		map.put("31", "#AA0000");
		map.put("32", "#00AA00");
		map.put("33", "#AA5500");
		map.put("34", "#0000AA");
		map.put("35", "#AA00AA");
		map.put("36", "#00AAAA");
		map.put("37", "#AAAAAA");
		map.put("1;30", "#555555");
		map.put("1;31", "#FF5555");
		map.put("1;32", "#55FF55");
		map.put("1;33", "#FFFF55");
		map.put("1;34", "#5555FF");
		map.put("1;35", "#FF55FF");
		map.put("1;36", "#55FFFF");
		map.put("1;37", "#FFFFFF");
		codeColorMap = Collections.unmodifiableMap(map);
	}

	private static final String SPAN_START = "<span style=\"color:%s\">";
	private static final String SPAN_END = "</span>";
	private static final char BASH_COLOR_START = 033;
	private static final char BASH_COLOR_END = 'm';
	private static final String BASH_COLOR_RESET = "0";

	public static String apply(String html) {	
		StringBuilder result = new StringBuilder();
		boolean insideSpan = false;
		String[] tokens = html.split(String.valueOf(BASH_COLOR_START));

		result.append(tokens[0]);

		for (int i = 1 ; i < tokens.length ; i++) {
			int endOfColor = tokens[i].indexOf(BASH_COLOR_END);
			String color = tokens[i].substring(1, endOfColor); // Strip '[' from start and 'm' from end
			StringBuilder replacement = new StringBuilder();
			if (insideSpan) {
				replacement.append(SPAN_END);
			}
			if (!color.equals(BASH_COLOR_RESET) && codeColorMap.containsKey(color)) {
				insideSpan = true;
				// XXX: Hack because GWT doesn't have String.format() :-/
				String colorSpan = SPAN_START;
				colorSpan = colorSpan.replace("%s", codeColorMap.get(color));
				replacement.append(colorSpan);
			} else {
				insideSpan = false;
			}
			result.append(replacement.toString());
			result.append(tokens[i].substring(endOfColor + 1));	
		}

		if (insideSpan) {
			result.append(SPAN_END);
		}

		return result.toString();
	}
}	
