package ro.pub.cs.vmchecker.client.ui;

import com.google.gwt.core.client.GWT;
import com.google.gwt.event.dom.client.ChangeEvent;
import com.google.gwt.event.dom.client.ChangeHandler;
import com.google.gwt.http.client.UrlBuilder;
import com.google.gwt.i18n.client.LocaleInfo;
import com.google.gwt.resources.client.ImageResource;
import com.google.gwt.event.dom.client.HasClickHandlers;
import com.google.gwt.event.dom.client.HasKeyPressHandlers;
import com.google.gwt.uibinder.client.UiBinder;
import com.google.gwt.uibinder.client.UiField;
import com.google.gwt.user.client.Command;
import com.google.gwt.user.client.DeferredCommand;
import com.google.gwt.user.client.Element;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.Composite;
import com.google.gwt.user.client.ui.HasText;
import com.google.gwt.user.client.ui.HTML;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.PasswordTextBox;
import com.google.gwt.user.client.ui.TextBox;
import com.google.gwt.user.client.ui.ListBox;
import com.google.gwt.user.client.ui.HorizontalPanel;
import com.google.gwt.user.client.ui.FlowPanel;
import com.google.gwt.user.client.ui.Image;
import com.google.gwt.user.client.ui.Widget;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.Window.Location;
import ro.pub.cs.vmchecker.client.i18n.LoginConstants;
import ro.pub.cs.vmchecker.client.ui.images.VmcheckerImages;
import ro.pub.cs.vmchecker.client.presenter.LoginPresenter;

public class LoginWidget extends Composite
 	implements LoginPresenter.Widget {

	private static LoginWidgetUiBinder uiBinder = GWT
			.create(LoginWidgetUiBinder.class);

	private static LoginConstants constants = GWT
			.create(LoginConstants.class);
	private static VmcheckerImages images = GWT
			.create(VmcheckerImages.class);

	interface LoginWidgetUiBinder extends UiBinder<Widget, LoginWidget> {
	}

	@UiField
	HTML loginDescription;

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
	
	@UiField
	Label formComment;

	@UiField
	Label formLabel;
	
	@UiField
	Label usernameLabel;
	
	@UiField
	Label passwordLabel;
	
	@UiField
	Image localeImage;
	
	@UiField
	ListBox localeBox;
	
	@UiField
	HorizontalPanel localeContainer;

	public LoginWidget() {
		initWidget(uiBinder.createAndBindUi(this));
		
		/* Setup the locale selection box */
		String[] locales = { "en", "ro" };

		localeContainer.getElement().setAttribute("align", "right");
		localeContainer.getElement().getFirstChildElement().getFirstChildElement().getFirstChildElement().setAttribute("style", "vertical-align: top; padding: 2px 5px;"); /* Center and align image */
		((Element)localeContainer.getElement().getFirstChildElement().getFirstChildElement().getLastChild()).setAttribute("style", "vertical-align: top; padding: 0px 20px 0px 0px;"); /* Center and align ListBox */
		localeImage.setResource(images.locale());
		localeBox.setWidth("200px");
		
		String currentLocale = LocaleInfo.getCurrentLocale().getLocaleName();
		if(currentLocale.equals("default"))
			currentLocale = "ro";
		
		for(String localeName : locales) {
			String nativeName = LocaleInfo.getLocaleNativeDisplayName(localeName);
			nativeName = (Character.toUpperCase(nativeName.charAt(0)) + nativeName.substring(1));
			localeBox.addItem(nativeName + " (" + localeName + ")", localeName);
			if(localeName.equals(currentLocale))
				localeBox.setSelectedIndex(localeBox.getItemCount() - 1);
		}
		
		localeBox.addChangeHandler(new ChangeHandler() {
			public void onChange(ChangeEvent event) {
				String localeName = localeBox.getValue(localeBox.getSelectedIndex());
				UrlBuilder builder = Location.createUrlBuilder().setParameter("locale",
					localeName);
				Window.Location.replace(builder.buildString());
			}
		});
		
		/* End locale selection box setup */
		
		loginDescription.setHTML(constants.loginDescription());
		formComment.setText(constants.formComment());
		formLabel.setText(constants.loginFormLabel());
		usernameLabel.setText(constants.usernameLabel());
		passwordLabel.setText(constants.passwordLabel());
		usernameComment.setVisible(false);
		passwordComment.setVisible(false);
		loginComment.setVisible(false);
		DeferredCommand.addCommand(new Command() {
			public void execute() {
				usernameField.setFocus(true);
			}
		});
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

	@Override
	public HasKeyPressHandlers[] getEnterSources() {
		HasKeyPressHandlers[] enterSources = {usernameField, passwordField, loginButton};
		return enterSources;
	}

}
