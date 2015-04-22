package ro.pub.cs.vmchecker.client.model;

import java.util.HashMap;

public class ResultInfo {

	public AccountType accountType;
	public String accountName;
	public HashMap<String, String> results;

	public ResultInfo(AccountType accountType, String accountName, HashMap<String, String> results) {
		this.accountType = accountType;
		this.accountName = accountName;
		this.results = results;
	}
}
