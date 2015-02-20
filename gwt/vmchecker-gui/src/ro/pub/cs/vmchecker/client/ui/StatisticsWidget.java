package ro.pub.cs.vmchecker.client.ui;

import java.util.ArrayList;

import com.google.gwt.core.client.GWT;
import com.google.gwt.resources.client.CssResource;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.FlowPanel;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.Anchor;
import com.google.gwt.user.client.ui.FlexTable;
import com.google.gwt.user.client.ui.HTMLTable;
import com.google.gwt.user.client.ui.Widget;

import ro.pub.cs.vmchecker.client.i18n.StatisticsConstants;
import ro.pub.cs.vmchecker.client.model.Assignment;
import ro.pub.cs.vmchecker.client.model.ResultInfo;
import ro.pub.cs.vmchecker.client.model.User;
import ro.pub.cs.vmchecker.client.presenter.StatisticsPresenter;

public class StatisticsWidget extends Composite implements StatisticsPresenter.Widget {

	private static StatisticsWidgetUiBinder uiBinder = GWT
			.create(StatisticsWidgetUiBinder.class);

	private static StatisticsConstants constants = GWT
			.create(StatisticsConstants.class);

	interface StatisticsWidgetUiBinder extends
			UiBinder<Widget, StatisticsWidget> {
	}

	interface Style extends CssResource {
		String table();
		String header();
		String name();
		String cell();
		String innercell();
		String oddrow();
		String evenrow();
		String itself();
		String subtitle();
	}

	@UiField
	FlowPanel panel;

	@UiField
	FlowPanel tablePanel;

	@UiField
	Label title;

	@UiField
	Label noSubmissionAvailableMessage;

	@UiField
	Label teamTitle;

	@UiField
	Label studentTitle;

	@UiField
	Style style;

	private FlexTable teamTable = new FlexTable();
	private FlexTable studentTable = new FlexTable();
	private VmcheckerPopup resultDetailsPopup;

	public StatisticsWidget() {
		initWidget(uiBinder.createAndBindUi(this));
		title.setText(constants.title());
		teamTitle.setText(constants.teams());
		studentTitle.setText(constants.individual());
		noSubmissionAvailableMessage.setText(constants.noSubmissionAvailable());
		resultDetailsPopup = new VmcheckerPopup();
		resultDetailsPopup.setStyleName("resultsPopup");
	}

	@Override
	public HTMLTable getTeamTable() {
		return teamTable;
	}

	@Override
	public HTMLTable getStudentTable() {
		return studentTable;
	}

	private void populateTable(HTMLTable table, User user, Assignment assignments[], ArrayList<ResultInfo> resultsInfo) {
		table.setCellPadding(5);
		table.setCellSpacing(0);
		table.setStyleName(style.table());
		table.getRowFormatter().setStyleName(0, style.header());
		table.getColumnFormatter().setStyleName(0, style.name());
		/* the first row is the header */
		int i = 0;
		for (int j = 0; j <= assignments.length; j++) {
			table.getCellFormatter().addStyleName(i, j, style.cell());
			if (j > 0) {
				table.setText(i, j, assignments[j-1].id);
			}
		}
		/* complete the content */
		for (i = 1; i <= resultsInfo.size(); i++) {
			ResultInfo result = resultsInfo.get(i - 1);
			for (int j = 0; j <= assignments.length; j++) {
				table.getCellFormatter().addStyleName(i, j, style.cell());
				/* the first column contains the student's name */
				if (j == 0) {
					table.getCellFormatter().addStyleName(i, j, style.name());
					table.setText(i, j, result.name);
				} else if (result.results.containsKey(assignments[j-1].id)) {
					table.getCellFormatter().addStyleName(i, j, style.innercell());
					table.setWidget(i, j, new Anchor(result.results.get(assignments[j-1].id)));
				}
			}

			if (user.name.equals(result.name) || user.id.equals(result.name)) {
				table.getRowFormatter().addStyleName(i, style.itself());
			} else {
				table.getRowFormatter().addStyleName(i, (i % 2 == 0) ? style.evenrow() : style.oddrow());
			}
		}

	}

	@Override
	public void displayInfo(User user, Assignment[] assignments,
			ArrayList<ResultInfo> teamResultsInfo, ArrayList<ResultInfo> studentResultsInfo) {
		tablePanel.clear();

		/* if there are no submissions to show, display the appropriate message. */
		if (teamResultsInfo.size() == 0 && studentResultsInfo.size() == 0) {
			tablePanel.add(noSubmissionAvailableMessage);
			return;
		}

		if (teamResultsInfo.size() != 0) {
			tablePanel.add(teamTitle);
			populateTable(teamTable, user, assignments, teamResultsInfo);
			tablePanel.add(teamTable);
		}

		if (studentResultsInfo.size() != 0) {
			tablePanel.add(studentTitle);
			populateTable(studentTable, user, assignments, studentResultsInfo);
			tablePanel.add(studentTable);
		}

	}

	@Override
	public void displayResultDetails(String htmlDetails) {
		resultDetailsPopup.showContent(htmlDetails);
	}


}

