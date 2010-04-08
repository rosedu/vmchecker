package ro.pub.cs.vmchecker.client;

import java.util.Date;

import com.google.gwt.user.client.Cookies;

/**
 * @author claudiugh
 *
 * This class handles persistent storage using cookie interface 
 * for several useful tokens 
 */
public class CookieManager {
	public static final String COURSE_COOKIE = "VMCHK-COURSE"; 
	public static final String USERNAME_COOKIE = "VMCHK-USER"; 
	
	/**
	 * the username is stored as cookie because it is obtained only 
	 * when login is successfully performed 
	 * @param username
	 */
	public static void saveUsername(String username) {
		Date now = new Date(); 
		Cookies.setCookie(USERNAME_COOKIE, username, new Date(now.getYear() + 1, now.getMonth(), now.getDay())); 		
	}
	
	public static String getUsername() {
		return Cookies.getCookie(USERNAME_COOKIE); 
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
	
}
