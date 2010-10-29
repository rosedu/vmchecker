package ro.pub.cs.vmchecker.client.presenter;

import ro.pub.cs.vmchecker.client.i18n.VmcheckerConstants;
import ro.pub.cs.vmchecker.client.event.StatusChangedEvent;
import ro.pub.cs.vmchecker.client.model.Assignment;
import ro.pub.cs.vmchecker.client.model.EvaluationResult;
import ro.pub.cs.vmchecker.client.model.StudentInfo;
import ro.pub.cs.vmchecker.client.service.HTTPService;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.event.shared.HandlerManager;
import com.google.gwt.user.client.rpc.AsyncCallback;
import com.google.gwt.user.client.ui.HTMLTable;
import com.google.gwt.user.client.ui.HasWidgets;

public class StatisticsPresenter implements Presenter {

	public interface Widget {
		HTMLTable getTable();
		void displayInfo(String username, Assignment[] assignments, StudentInfo[] studentInfo);
		void displayResultDetails(String htmlDetails);
	}

	private HandlerManager eventBus;
	private HTTPService service;
	private static VmcheckerConstants constants = GWT
			.create(VmcheckerConstants.class);
	private HasWidgets container;
	private StatisticsPresenter.Widget widget;

	private String courseId;
	private String username;
	private Assignment[] assignments;
	private StudentInfo[] studentsInfo;

	public StatisticsPresenter(HandlerManager eventBus, HTTPService service,
			String courseId, String username, Assignment[] assignments, StatisticsPresenter.Widget widget) {
		this.eventBus = eventBus;
		this.service = service;
		this.courseId = courseId;
		this.assignments = assignments;
		this.username = username;
		bindWidget(widget);
		listenTableEvents();
	}

	private void listenTableEvents() {
		widget.getTable().addClickHandler(new ClickHandler() {

			@Override
			public void onClick(ClickEvent event) {
				HTMLTable.Cell cell = widget.getTable().getCellForEvent(event);
				if (cell != null) {
					StudentInfo studentInfo = studentsInfo[cell.getRowIndex() - 1];
					String assignmentId = assignments[cell.getCellIndex() - 1].id;
					if (studentInfo.results.containsKey(assignmentId)) {
						loadAndShowResultDetails(assignmentId, studentInfo.id);
					}
				}
			}

		});
	}

	private void loadAndShowResultDetails(String assignmentId, String username) {
		eventBus.fireEvent(new StatusChangedEvent(StatusChangedEvent.StatusType.ACTION,
		constants.loadResults()));
		service.getUserResults(courseId, assignmentId, username, new AsyncCallback<EvaluationResult[]> () {

			@Override
			public void onFailure(Throwable caught) {
				GWT.log("StatisticsPresenter.loadAndShowResultDetails()", caught);
			}

			@Override
			public void onSuccess(EvaluationResult[] result) {
				eventBus.fireEvent(new StatusChangedEvent(StatusChangedEvent.StatusType.RESET, null));
				String resultsHTML = "";
				for (int i = 0; i < result.length; i++) {
					resultsHTML += result[i].toHTML();
				}
				widget.displayResultDetails(resultsHTML);
			}

		});
	}

	private void bindWidget(StatisticsPresenter.Widget widget) {
		this.widget = widget;
	}

	@Override
	public void clearEventHandlers() {

	}

	@Override
	public void go(final HasWidgets container) {
		this.container = container;
		eventBus.fireEvent(new StatusChangedEvent(StatusChangedEvent.StatusType.ACTION,
				constants.loadStatistics()));
		service.getAllResults(courseId, new AsyncCallback<StudentInfo[]>() {

			@Override
			public void onFailure(Throwable caught) {
				GWT.log("StatisticsPresenter.getAllResults()", caught);
			}

			@Override
			public void onSuccess(StudentInfo[] result) {
				container.clear();
				studentsInfo = result;
				widget.displayInfo(username, assignments, result);
				container.add((com.google.gwt.user.client.ui.Widget) widget);
				eventBus.fireEvent(new StatusChangedEvent(StatusChangedEvent.StatusType.RESET, null));
			}

		});

	}

}
