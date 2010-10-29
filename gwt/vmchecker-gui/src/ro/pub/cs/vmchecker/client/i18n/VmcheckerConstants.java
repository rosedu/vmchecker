package ro.pub.cs.vmchecker.client.i18n;

import com.google.gwt.core.client.GWT;
import com.google.gwt.i18n.client.Constants;

public interface VmcheckerConstants extends Constants,
				AssignmentConstants, LoginConstants,
				HeaderConstants, UploadConstants {

	String serviceError();
	String unknownFormat();
	String popupCloseButton();

	String statisticsTitle();
}
