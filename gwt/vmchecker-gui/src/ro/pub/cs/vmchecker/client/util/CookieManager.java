package ro.pub.cs.vmchecker.client.util;

import java.util.Date;

import com.google.gwt.user.client.Cookies;

import ro.pub.cs.vmchecker.client.model.User;

/**
 * @author claudiugh
 *
 * This class handles persistent storage using cookie interface 
 * for several useful tokens 
 */
public class CookieManager {
	public static final String COURSE_COOKIE = "VMCHK-COURSE"; 
	public static final String USERNAME_COOKIE = "VMCHK-USER-NAME";
	public static final String USERID_COOKIE = "VMCHK-USER-ID";
	public static final String[] cookies = { COURSE_COOKIE, USERNAME_COOKIE, USERID_COOKIE };
	
	/**
	 * the user name and id are stored as cookie because it is obtained only
	 * when login is successfully performed 
	 * @param username
	 */
	public static void saveUser(User user) {
		Date now = new Date(); 
		Cookies.setCookie(USERNAME_COOKIE, user.name, new Date(now.getYear() + 1, now.getMonth(), now.getDay())); 
		Cookies.setCookie(USERID_COOKIE, user.id, new Date(now.getYear() + 1, now.getMonth(), now.getDay())); 
	}
	
	public static User getUser() {
		String userId = Cookies.getCookie(USERID_COOKIE);
		String userName = Cookies.getCookie(USERNAME_COOKIE);

		/*
		 * A user must have a valid id.
		 */
		if (userId == null)
			return null;

		if (userName == null)
			userName = "";

		return new User(userId, userName);
	}
	
	/**
	 * the courseId is stored in order to restore the last 
	 * course view after an active sessions ends 
	 * @param courseId
	 */
	public static void saveLastCourse(String courseId) {
		Date now = new Date(); 
		Cookies.setCookie(COURSE_COOKIE, courseId, new Date(now.getYear() + 1, now.getMonth(), now.getDay())); 				
	}

	public static String getLastCourse() {
		return Cookies.getCookie(COURSE_COOKIE);
	}

	public static void clearCookies() {
		for (String cookie : cookies) {
			Cookies.removeCookie(cookie);
		}
	}
	
}
