package ro.pub.cs.vmchecker.client.ui;

import com.google.gwt.core.client.GWT;
import com.google.gwt.resources.client.CssResource;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.FlowPanel;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.Anchor;
import com.google.gwt.user.client.ui.Grid;
import com.google.gwt.user.client.ui.HTMLTable;
import com.google.gwt.user.client.ui.Widget;

import ro.pub.cs.vmchecker.client.i18n.VmcheckerConstants;
import ro.pub.cs.vmchecker.client.model.Assignment;
import ro.pub.cs.vmchecker.client.model.StudentInfo;
import ro.pub.cs.vmchecker.client.model.User;
import ro.pub.cs.vmchecker.client.presenter.StatisticsPresenter;

public class StatisticsWidget extends Composite implements StatisticsPresenter.Widget {

	private static StatisticsWidgetUiBinder uiBinder = GWT
			.create(StatisticsWidgetUiBinder.class);

	private static VmcheckerConstants constants = GWT
			.create(VmcheckerConstants.class);

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
	Style style;

	private Grid table = new Grid();
	private VmcheckerPopup resultDetailsPopup;

	public StatisticsWidget() {
		initWidget(uiBinder.createAndBindUi(this));
		title.setText(constants.statisticsTitle());
		noSubmissionAvailableMessage.setText(constants.statisticsNoSubmissionAvailable());
		resultDetailsPopup = new VmcheckerPopup();
		resultDetailsPopup.setStyleName("resultsPopup");
	}

	@Override
	public HTMLTable getTable() {
		return table;
	}

	@Override
	public void displayInfo(User user, Assignment[] assignments, StudentInfo[] studentInfo) {
		tablePanel.clear();
		table.resize(studentInfo.length + 1, assignments.length + 1);
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
		for (i = 1; i <= studentInfo.length; i++) {
			StudentInfo student = studentInfo[i - 1];
			for (int j = 0; j <= assignments.length; j++) {
				table.getCellFormatter().addStyleName(i, j, style.cell());
				/* the first column contains the student's name */
				if (j == 0) {
					table.getCellFormatter().addStyleName(i, j, style.name());
					table.setText(i, j, student.name);
				} else if (student.results.containsKey(assignments[j-1].id)) {
					table.getCellFormatter().addStyleName(i, j, style.innercell());
					//table.setText(i, j, student.results.get(assignments[j-1].id));
					table.setWidget(i, j, new Anchor(student.results.get(assignments[j-1].id)));
				}
			}

			if (user.name.equals(student.name) || user.id.equals(student.name)) {
				table.getRowFormatter().addStyleName(i, style.itself());
			} else {
				table.getRowFormatter().addStyleName(i, (i % 2 == 0) ? style.evenrow() : style.oddrow());
			}
		}
		/* if there are no submissions to show, display the appropriate message. */
		if (studentInfo.length == 0) {
			tablePanel.add(noSubmissionAvailableMessage);
		} else {
			/* add the table */
			tablePanel.add(table);
		}
	}

	@Override
	public void displayResultDetails(String htmlDetails) {
		resultDetailsPopup.showContent(htmlDetails);
	}


}

