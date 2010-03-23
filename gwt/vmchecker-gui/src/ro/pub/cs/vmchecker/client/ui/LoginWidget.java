package ro.pub.cs.vmchecker.client.ui;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.HasClickHandlers;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.HasText;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.PasswordTextBox;
import com.google.gwt.user.client.ui.TextBox;
import com.google.gwt.user.client.ui.Widget;
import ro.pub.cs.vmchecker.client.presenter.LoginPresenter;

public class LoginWidget extends Composite
 	implements LoginPresenter.Widget {

	private static LoginWidgetUiBinder uiBinder = GWT
			.create(LoginWidgetUiBinder.class);

	interface LoginWidgetUiBinder extends UiBinder<Widget, LoginWidget> {
	}

	@UiField
	TextBox usernameField;
	
	@UiField 
	Label usernameComment; 
	
	@UiField 
	PasswordTextBox passwordField; 
	
	@UiField
	Label passwordComment; 
	
	@UiField 
	Button loginButton; 
	
	@UiField
	Label loginComment; 
	
	public LoginWidget() {
		initWidget(uiBinder.createAndBindUi(this));
		usernameComment.setVisible(false); 
		passwordComment.setVisible(false); 
		loginComment.setVisible(false); 
	}

	@Override
	public HasClickHandlers getLoginButton() {
		return loginButton; 
	}

	@Override
	public HasText getPasswordField() {
		return passwordField; 
	}

	@Override
	public HasText getUsernameField() {
		return usernameField; 
	}

	@Override
	public HasText getPasswordCommentLabel() {
		return passwordComment; 
	}

	@Override
	public HasText getUsernameCommentLabel() {
		return usernameComment; 
	}

	@Override
	public HasText getLoginCommentLabel() {
		return loginComment;
	}

	@Override
	public void setInputsEnabled(boolean enabled) {
		usernameField.setEnabled(enabled); 
		passwordField.setEnabled(enabled); 
		loginButton.setEnabled(enabled); 
	}

	@Override
	public void setLoginCommentVisible(boolean visible) {
		loginComment.setVisible(visible); 
	}

	@Override
	public void setPasswordCommentVisible(boolean visible) {
		passwordComment.setVisible(visible); 
	}

	@Override
	public void setUsernameCommentVisible(boolean visible) {
		usernameComment.setVisible(visible); 
	}

}
