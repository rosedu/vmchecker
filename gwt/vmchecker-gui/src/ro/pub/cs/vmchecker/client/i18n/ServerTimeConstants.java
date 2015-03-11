package ro.pub.cs.vmchecker.client.i18n;

import com.google.gwt.core.client.GWT;
import com.google.gwt.i18n.client.Constants;

public interface ServerTimeConstants extends Constants {

	String serverTimeMsg();
	String browserTimeAheadMsg();
	String browserTimeBehindMsg();

	String hours();
	String hour();
	String minutes();
	String minute();
	String seconds();
	String second();
	String and();
	String lessThanASecond();
}
