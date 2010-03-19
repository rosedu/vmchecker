package ro.pub.cs.vmchecker.client.presenter;

import ro.pub.cs.vmchecker.client.event.AuthenticationEvent;
import ro.pub.cs.vmchecker.client.model.AuthenticationResponse;
import ro.pub.cs.vmchecker.client.service.HTTPService;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.event.dom.client.HasClickHandlers;
import com.google.gwt.event.shared.HandlerManager;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.rpc.AsyncCallback;
import com.google.gwt.user.client.ui.HasText;
import com.google.gwt.user.client.ui.HasWidgets;

public class LoginPresenter implements Presenter {

	public interface Widget {
		HasText getUsernameField(); 
		HasText getUsernameCommentLabel(); 
		HasText getPasswordField(); 
		HasText getPasswordCommentLabel(); 
		HasClickHandlers getLoginButton();
		HasText getLoginCommentLabel();
		void setInputsEnabled(boolean enabled); 
	}
	
	private HandlerManager eventBus; 
	private HTTPService service; 
	private Widget widget; 
	
	public LoginPresenter(HandlerManager eventBus, HTTPService service, Widget widget) {
		this.eventBus = eventBus; 
		this.service = service;
		bindWidget(widget); 
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
			widget.getUsernameCommentLabel().setText("Utilizator necompletat");
			valid = false; 
		} else {
			widget.getUsernameCommentLabel().setText("");
		}
		
		/* password */
		if (!validatePassword(widget.getPasswordField().getText())) {
			widget.getPasswordCommentLabel().setText("Parola necompletata");
			valid = false; 
		} else {
			widget.getPasswordCommentLabel().setText(""); 
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
				this.widget.getPasswordField().getText(), new AsyncCallback<AuthenticationResponse>() {

					@Override
					public void onFailure(Throwable caught) {
						Window.alert(caught.getMessage());
						widget.setInputsEnabled(true); 
					}

					@Override
					public void onSuccess(AuthenticationResponse result) {
						if (result.status) {
							/* send authentication event */
							AuthenticationEvent authEvent = new AuthenticationEvent(result.username);
							eventBus.fireEvent(authEvent); 
						} else {
							widget.getLoginCommentLabel().setText(result.info);
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

}
