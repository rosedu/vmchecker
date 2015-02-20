package ro.pub.cs.vmchecker.client.presenter;

import java.util.ArrayList;

import ro.pub.cs.vmchecker.client.i18n.VmcheckerConstants;
import ro.pub.cs.vmchecker.client.event.StatusChangedEvent;
import ro.pub.cs.vmchecker.client.model.Assignment;
import ro.pub.cs.vmchecker.client.model.EvaluationResult;
import ro.pub.cs.vmchecker.client.model.ResultInfo;
import ro.pub.cs.vmchecker.client.model.User;
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
		HTMLTable getTeamTable();
		HTMLTable getStudentTable();
		void displayInfo(User user, Assignment[] assignments,
			ArrayList<ResultInfo> teamResultInfo, ArrayList<ResultInfo> studentResultInfo);
		void displayResultDetails(String htmlDetails);
	}

	private class TableClickHandler implements ClickHandler {
		final HTMLTable table;
		final ArrayList<ResultInfo> resultsInfo;

		public TableClickHandler(HTMLTable table, ArrayList<ResultInfo> resultsInfo) {
			this.table = table;
			this.resultsInfo = resultsInfo;
		}

		@Override
		public void onClick(ClickEvent event) {
			HTMLTable.Cell cell = this.table.getCellForEvent(event);
			if (cell != null) {
				GWT.log("Click for cell " + cell, null);
				ResultInfo resultInfo = this.resultsInfo.get(cell.getRowIndex() - 1);
				String assignmentId = assignments[cell.getCellIndex() - 1].id;
				if (resultInfo.results.containsKey(assignmentId)) {
					if (resultInfo.owner == ResultInfo.OwnerType.USER) {
						loadAndShowUserResultDetails(assignmentId, resultInfo.name);
					} else {
						loadAndShowTeamResultDetails(assignmentId, resultInfo.name);
					}
				}
			}
		}
	}


	private HandlerManager eventBus;
	private HTTPService service;
	private static VmcheckerConstants constants = GWT
			.create(VmcheckerConstants.class);
	private HasWidgets container;
	private StatisticsPresenter.Widget widget;

	private String courseId;
	private User user;
	private Assignment[] assignments;
	private ArrayList<ResultInfo> teamResultsInfo, studentResultsInfo;

	public StatisticsPresenter(HandlerManager eventBus, HTTPService service,
			String courseId, User user, Assignment[] assignments, StatisticsPresenter.Widget widget) {
		this.eventBus = eventBus;
		this.service = service;
		this.courseId = courseId;
		this.assignments = assignments;
		this.user = user;
		this.teamResultsInfo = new ArrayList<ResultInfo>();
		this.studentResultsInfo = new ArrayList<ResultInfo>();
		bindWidget(widget);
		listenTableEvents();
	}

	private void listenTableEvents() {
		widget.getTeamTable().addClickHandler(new TableClickHandler(widget.getTeamTable(), teamResultsInfo));
		widget.getStudentTable().addClickHandler(new TableClickHandler(widget.getStudentTable(), studentResultsInfo));
	}

	private void loadAndShowTeamResultDetails(String assignmentId, String teamname) {
		eventBus.fireEvent(new StatusChangedEvent(StatusChangedEvent.StatusType.ACTION,
		constants.loadResults()));
		service.getTeamResults(courseId, assignmentId, teamname, new AsyncCallback<EvaluationResult[]> () {

			@Override
			public void onFailure(Throwable caught) {
				GWT.log("StatisticsPresenter.loadAndShowTeamResultDetails()", caught);
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

	private void loadAndShowUserResultDetails(String assignmentId, String username) {
		eventBus.fireEvent(new StatusChangedEvent(StatusChangedEvent.StatusType.ACTION,
		constants.loadResults()));
		service.getUserResults(courseId, assignmentId, username, new AsyncCallback<EvaluationResult[]> () {

			@Override
			public void onFailure(Throwable caught) {
				GWT.log("StatisticsPresenter.loadAndShowUserResultDetails()", caught);
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

	private void processResults(ResultInfo[] resultsInfo) {
		studentResultsInfo.clear();
		teamResultsInfo.clear();
		for (ResultInfo result : resultsInfo) {
			if (result.owner == ResultInfo.OwnerType.USER) {
				studentResultsInfo.add(result);
			}

			if (result.owner == ResultInfo.OwnerType.TEAM) {
				teamResultsInfo.add(result);
			}
		}
	}

	@Override
	public void go(final HasWidgets container) {
		this.container = container;
		eventBus.fireEvent(new StatusChangedEvent(StatusChangedEvent.StatusType.ACTION,
				constants.loadStatistics()));
		service.getAllResults(courseId, new AsyncCallback<ResultInfo[]>() {

			@Override
			public void onFailure(Throwable caught) {
				GWT.log("StatisticsPresenter.getAllResults()", caught);
			}

			@Override
			public void onSuccess(ResultInfo[] result) {
				container.clear();
				processResults(result);
				widget.displayInfo(user, assignments, teamResultsInfo, studentResultsInfo);
				container.add((com.google.gwt.user.client.ui.Widget) widget);
				eventBus.fireEvent(new StatusChangedEvent(StatusChangedEvent.StatusType.RESET, null));
			}

		});

	}

}
