package ro.pub.cs.vmchecker.client.presenter;

import ro.pub.cs.vmchecker.client.i18n.LoginConstants;
import ro.pub.cs.vmchecker.client.event.AuthenticationEvent;
import ro.pub.cs.vmchecker.client.model.AuthenticationResponse;
import ro.pub.cs.vmchecker.client.service.HTTPService;

import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.event.dom.client.HasClickHandlers;
import com.google.gwt.event.dom.client.HasKeyPressHandlers;
import com.google.gwt.event.dom.client.KeyCodes;
import com.google.gwt.event.dom.client.KeyPressEvent;
import com.google.gwt.event.dom.client.KeyPressHandler;
import com.google.gwt.event.shared.EventBus;
import com.google.gwt.core.client.GWT;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.rpc.AsyncCallback;
import com.google.gwt.user.client.ui.HasText;
import com.google.gwt.user.client.ui.HasValue;
import com.google.gwt.user.client.ui.HasWidgets;

public class LoginPresenter implements Presenter, KeyPressHandler {

	public interface Widget {
		HasText getUsernameField();
		HasText getUsernameCommentLabel();
		void setUsernameCommentVisible(boolean visible);
		HasText getPasswordField();
		HasText getPasswordCommentLabel();
		void setPasswordCommentVisible(boolean visible);
		HasValue<Boolean> getExtendSessionField();
		HasClickHandlers getLoginButton();
		HasText getLoginCommentLabel();
		void setLoginCommentVisible(boolean visible);
		void setInputsEnabled(boolean enabled);
		HasKeyPressHandlers[] getEnterSources();
	}

	private EventBus eventBus;
	private HTTPService service;
	private static LoginConstants constants = GWT
			.create(LoginConstants.class);
	private Widget widget;

	public LoginPresenter(EventBus eventBus, HTTPService service, Widget widget) {
		this.eventBus = eventBus;
		this.service = service;
		bindWidget(widget);
		listenEnterPress();
	}

	private void listenEnterPress() {
		HasKeyPressHandlers[] enterSources = widget.getEnterSources();
		for (int i = 0; i < enterSources.length; i++) {
			enterSources[i].addKeyPressHandler(this);
		}
	}

	private boolean validateUsername(String username) {
		return !username.isEmpty();
	}

	private boolean validatePassword(String password) {
		return !password.isEmpty();
	}

	private boolean validateFields() {
		boolean valid = true;
		/* username */
		if (!validateUsername(widget.getUsernameField().getText())) {
			widget.getUsernameCommentLabel().setText(constants.usernameEmpty());
			widget.setUsernameCommentVisible(true);
			valid = false;
		} else {
			widget.getUsernameCommentLabel().setText("");
			widget.setUsernameCommentVisible(false);
		}

		/* password */
		if (!validatePassword(widget.getPasswordField().getText())) {
			widget.getPasswordCommentLabel().setText(constants.passwordEmpty());
			widget.setPasswordCommentVisible(true);
			valid = false;
		} else {
			widget.getPasswordCommentLabel().setText("");
			widget.setPasswordCommentVisible(false);
		}
		return valid;
	}

	private void bindWidget(Widget widget) {
		this.widget = widget;
		widget.getLoginButton().addClickHandler(new ClickHandler() {

			@Override
			public void onClick(ClickEvent event) {
				if (validateFields()) {
					sendAuthenticationRequest();
				}
			}

		});
	}

	private void sendAuthenticationRequest() {
		widget.setInputsEnabled(false);
		service.performAuthentication(this.widget.getUsernameField().getText(),
									  this.widget.getPasswordField().getText(),
									  this.widget.getExtendSessionField().getValue(),
									  new AsyncCallback<AuthenticationResponse>() {

					@Override
					public void onFailure(Throwable caught) {
						Window.alert(caught.getMessage());
						widget.setInputsEnabled(true);
					}

					@Override
					public void onSuccess(AuthenticationResponse result) {
						if (result.status) {
							/* send authentication event */
							AuthenticationEvent authEvent = new AuthenticationEvent(result.user);
							eventBus.fireEvent(authEvent);
						} else {
							widget.getLoginCommentLabel().setText(result.info);
							widget.setLoginCommentVisible(true);
							widget.setInputsEnabled(true);
						}
					}
		});
	}

	@Override
	public void clearEventHandlers() {
	}

	@Override
	public void go(HasWidgets container) {
		container.add((com.google.gwt.user.client.ui.Widget) widget);
	}

	@Override
	public void onKeyPress(KeyPressEvent event) {
		if (KeyCodes.KEY_ENTER == event.getCharCode() ||
			KeyCodes.KEY_ENTER == event.getNativeEvent().getKeyCode()) {
			/* enter was pressed, send the request */
			if (validateFields()) {
				sendAuthenticationRequest();
			}
		}
	}

}
