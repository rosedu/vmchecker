package ro.pub.cs.vmchecker.client.presenter;

import ro.pub.cs.vmchecker.client.i18n.VmcheckerConstants;
import ro.pub.cs.vmchecker.client.event.AssignmentSelectedEvent;
import ro.pub.cs.vmchecker.client.event.AssignmentSelectedEventHandler;
import ro.pub.cs.vmchecker.client.event.AuthenticationEvent;
import ro.pub.cs.vmchecker.client.event.ErrorDisplayEvent;
import ro.pub.cs.vmchecker.client.event.StatusChangedEvent;
import ro.pub.cs.vmchecker.client.model.Assignment;
import ro.pub.cs.vmchecker.client.model.ErrorResponse;
import ro.pub.cs.vmchecker.client.model.EvaluationResult;
import ro.pub.cs.vmchecker.client.service.HTTPService;
import ro.pub.cs.vmchecker.client.service.ServiceError;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.logical.shared.HasSelectionHandlers;
import com.google.gwt.event.logical.shared.SelectionEvent;
import com.google.gwt.event.logical.shared.SelectionHandler;
import com.google.gwt.event.shared.EventBus;
import com.google.gwt.event.shared.HandlerRegistration;
import com.google.gwt.user.client.rpc.AsyncCallback;
import com.google.gwt.user.client.ui.FormPanel;
import com.google.gwt.user.client.ui.HasHTML;
import com.google.gwt.user.client.ui.HasText;
import com.google.gwt.user.client.ui.HasWidgets;
import com.google.gwt.user.client.ui.Hidden;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.ui.FormPanel.SubmitCompleteEvent;
import com.google.gwt.user.client.ui.FormPanel.SubmitCompleteHandler;

public class AssignmentBoardPresenter implements Presenter {

	public interface Widget {
		public static enum View {
			STATEMENT, UPLOAD, RESULTS
		};

		public static final String[] viewTitles = { "viewTitlesStatement", "viewTitlesSolution", "viewTitlesResults" };

		public static final int defaultView = 0; /* STATEMENT */

		HasText getTitleLabel();
		HasText getDeadlineLabel();
		HasSelectionHandlers<Integer> getMenu();
		void setSelectedTab(int tabIndex);
		void displayView(com.google.gwt.user.client.ui.Widget view);
		HasWidgets getViewStack();
	}

	public interface StatementWidget {
		void setStatementHref(String statementHref);
	}

	public interface ResultsWidget {
		HasHTML getResultContainer();
	}

	private EventBus eventBus;
	private HTTPService service;
	private static VmcheckerConstants constants = GWT
			.create(VmcheckerConstants.class);
	private AssignmentBoardPresenter.Widget widget;
	private UploadPresenter uploadPresenter = null;
	private HasWidgets container;
	private HandlerRegistration assignmentSelectReg = null;
	private String courseId;
	private Assignment assignment;

	private StatementWidget statementWidget = new ro.pub.cs.vmchecker.client.ui.StatementWidget();
	private ResultsWidget resultsWidget = new ro.pub.cs.vmchecker.client.ui.ResultsWidget();

	public AssignmentBoardPresenter(EventBus eventBus, HTTPService service, String courseId, AssignmentBoardPresenter.Widget widget) {

		this.eventBus = eventBus;
		this.service = service;
		this.courseId = courseId;
		uploadPresenter = new UploadPresenter(eventBus, service);
		bindWidget(widget);

	}

	public void listenAssignmentSelect() {
		assignmentSelectReg = eventBus.addHandler(AssignmentSelectedEvent.TYPE, new AssignmentSelectedEventHandler() {
			public void onSelect(AssignmentSelectedEvent event) {
				container.clear();
				((com.google.gwt.user.client.ui.Widget)widget).setVisible(false);
				container.add((com.google.gwt.user.client.ui.Widget)widget);
				assignmentSelected(event.data);
			}
		});
	}

	public void assignmentSelected(Assignment data) {
		statementWidget.setStatementHref(data.statementLink);
		widget.getTitleLabel().setText(data.title);
		this.assignment = data;
		widget.getDeadlineLabel().setText(data.deadline);
		setVisibleView(Widget.defaultView);
		widget.setSelectedTab(Widget.defaultView);
		uploadPresenter.setParameters(courseId, assignment);
		((com.google.gwt.user.client.ui.Widget)widget).setVisible(true);
	}

	public void setVisibleView(int viewIndex) {
		Widget.View view = Widget.View.values()[viewIndex];
		switch (view) {
		case UPLOAD:
			uploadPresenter.loadAndDisplayUpload();
			break;
		case STATEMENT:
			loadAndDisplayStatement();
			break;
		case RESULTS:
			loadAndDisplayResults();
			break;
		}
	}

	private void loadAndDisplayResults() {
		eventBus.fireEvent(new StatusChangedEvent(StatusChangedEvent.StatusType.ACTION,
		constants.loadResults()));

		service.getResults(courseId, assignment.id, new AsyncCallback<EvaluationResult[]>() {

			public void onFailure(Throwable caught) {
				GWT.log("[AssignmentBoardPresenter]", caught);
				eventBus.fireEvent(new ErrorDisplayEvent(constants.loadResultsFail(), caught.getMessage()));
			}

			public void onSuccess(EvaluationResult[] result) {
				String resultHTML = "";
				for (int i = 0; i < result.length; i++) {
					EvaluationResult resultPack = result[i];
					resultHTML += resultPack.toHTML();
				}
				resultsWidget.getResultContainer().setHTML(resultHTML);
				widget.displayView((com.google.gwt.user.client.ui.Widget) resultsWidget);
				eventBus.fireEvent(new StatusChangedEvent(
						StatusChangedEvent.StatusType.RESET, ""));
			}
		});

	}

	private void loadAndDisplayStatement() {
		widget.displayView((com.google.gwt.user.client.ui.Widget) statementWidget);
	}

	private void bindWidget(AssignmentBoardPresenter.Widget widget) {
		this.widget = widget;
		uploadPresenter.go(widget.getViewStack());
		listenMenuSelection();
		listenAssignmentSelect();
	}


	private void listenMenuSelection() {
		widget.getMenu().addSelectionHandler(new SelectionHandler<Integer> () {

			public void onSelection(SelectionEvent<Integer> event) {
				setVisibleView(event.getSelectedItem().intValue());
			}
		});
	}

	@Override
	public void go(HasWidgets container) {
		this.container = container;
	}

	@Override
	public void clearEventHandlers() {
		assignmentSelectReg.removeHandler();
	}

}
