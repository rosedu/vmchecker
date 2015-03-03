package ro.pub.cs.vmchecker.client.model;

import java.util.HashMap;

public class ResultInfo {

	public enum OwnerType {
		USER,
		TEAM
	};

	public OwnerType owner;
	public String name;
	public HashMap<String, String> results;

	public ResultInfo(OwnerType owner, String name, HashMap<String, String> results) {
		this.owner = owner;
		this.name = name;
		this.results = results;
	}
}
