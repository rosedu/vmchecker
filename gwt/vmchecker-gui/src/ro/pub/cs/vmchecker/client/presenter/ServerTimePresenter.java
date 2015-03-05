package ro.pub.cs.vmchecker.client.presenter;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.Date;

import ro.pub.cs.vmchecker.client.event.ServerTimeUpdateEvent;
import ro.pub.cs.vmchecker.client.event.ServerTimeUpdateEventHandler;
import ro.pub.cs.vmchecker.client.i18n.ServerTimeConstants;

import com.google.gwt.event.dom.client.ChangeEvent;
import com.google.gwt.event.dom.client.ChangeHandler;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.event.dom.client.HasChangeHandlers;
import com.google.gwt.event.dom.client.HasClickHandlers;
import com.google.gwt.event.shared.EventBus;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.Timer;
import com.google.gwt.user.client.rpc.AsyncCallback;
import com.google.gwt.user.client.ui.HasText;
import com.google.gwt.user.client.ui.HasWidgets;
import com.google.gwt.user.client.ui.Widget;
import com.google.gwt.i18n.shared.DateTimeFormat;

import com.google.gwt.core.client.GWT;
public class ServerTimePresenter implements Presenter {

	private EventBus eventBus;
	private ServerTimePresenter.Widget widget; 
	private Date serverTime;
	private DateTimeFormat dtf = DateTimeFormat.getFormat("HH:mm:ss, dd MMMM yyyy");
	private Timer clockTimer;
	
	private static ServerTimeConstants constants = GWT
			.create(ServerTimeConstants.class);
	
	public interface Widget {
		HasText getServerTime();
		HasText getBrowserTimeOffsetMsg();
		HasText getBrowserTimeOffset();
	}
	
	public ServerTimePresenter(EventBus eventBus, ServerTimePresenter.Widget widget) {
		this.eventBus = eventBus; 
		this.widget = widget; 
		this.serverTime = new Date(0);
		listenServerTimeUpdate();
		launchClockUpdateTimer();
	}

	private void updateDisplayedTime(Date newTime) {
		widget.getServerTime().setText(dtf.format(newTime));
	}

	private void updateDisplayedOffset(Date serverTime) {
		Date browserTime = new Date();
		if (serverTime.compareTo(browserTime) < 0) {
			widget.getBrowserTimeOffsetMsg().setText(constants.browserTimeAheadMsg());
			widget.getBrowserTimeOffset().setText(formatDuration(browserTime.getTime(), serverTime.getTime()));
		} else {
			widget.getBrowserTimeOffsetMsg().setText(constants.browserTimeBehindMsg());
			widget.getBrowserTimeOffset().setText(formatDuration(serverTime.getTime(), browserTime.getTime()));
		}
	}

	private String formatDuration(long time1, long time2) {
		long diff = time1 - time2;
		long diffSecs = (diff / 1000) % 60;
		long diffMins = ((diff / 1000) / 60) % 60;
		long diffHours = (((diff / 1000) / 60) / 60);
		if (diffHours == 0 && diffMins == 0 && diffSecs == 0) {
			return constants.lessThanASecond();
		}
		StringBuilder sb = new StringBuilder();
		if (diffHours > 0) {
			sb.append(diffHours);
			sb.append(" ");
			if (diffHours == 1) {
				sb.append(constants.hour());
			} else {
				sb.append(constants.hours());
			}
		}
		if (sb.length() > 0 && diffMins > 0 && diffSecs > 0) {
			sb.append(", ");
		} else if (sb.length() > 0 && (diffMins > 0 || diffSecs > 0)) {
			sb.append(" ");
			sb.append(constants.and());
			sb.append(" ");

		}
		if (diffMins > 0) {
			sb.append(diffMins);
			sb.append(" ");
			if (diffMins == 1) {
				sb.append(constants.minute());
			} else {
				sb.append(constants.minutes());
			}
		}
		if (sb.length() > 0 && diffSecs > 0) {
			sb.append(" ");
			sb.append(constants.and());
			sb.append(" ");

		}
		if (diffSecs > 0) {
			sb.append(diffSecs);
			sb.append(" ");
			if (diffSecs == 1) {
				sb.append(constants.second());
			} else {
				sb.append(constants.seconds());
			}
		}
		return sb.toString();
	}

	private void listenServerTimeUpdate() {
		this.eventBus.addHandler(ServerTimeUpdateEvent.TYPE, new ServerTimeUpdateEventHandler() {
			public void onServerTimeUpdate(ServerTimeUpdateEvent event) {
				ServerTimePresenter.this.serverTime = event.getDate();
				updateDisplayedTime(ServerTimePresenter.this.serverTime);
				updateDisplayedOffset(ServerTimePresenter.this.serverTime);
			}
		}); 
	}

	private void launchClockUpdateTimer() {
		clockTimer = new Timer() {
			@Override
			public void run() {
				serverTime.setTime(serverTime.getTime() + 1000);
				updateDisplayedTime(serverTime);
			}
		};

		clockTimer.scheduleRepeating(1000);
	}
	
	public Widget getWidget() {
		return (Widget) widget; 
	}

	@Override
	public void go(HasWidgets container) {
		container.add((com.google.gwt.user.client.ui.Widget)widget);  
	}

	@Override
	public void clearEventHandlers() {
		if (clockTimer != null) {
			clockTimer.cancel();
		}
	}
	
	
}
