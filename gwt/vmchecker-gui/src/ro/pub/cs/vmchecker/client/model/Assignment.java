package ro.pub.cs.vmchecker.client.model;

public class Assignment {
	public enum StorageType {
		NORMAL,
		LARGE
	};

	public String id;
	public String title;
	public StorageType storageType;
	public String storageHost;
	public String storageBasepath;
	public String deadline;
	public String statementLink;
	public boolean hasTeam;
	public String team;

	public Assignment(String id, String title, StorageType storageType,
			String storageHost, String storageBasepath,
			String deadline, String statementLink,
			boolean hasTeam, String team) {
		this.id = id;
		this.title = title;
		this.storageType = storageType;
		this.storageHost = storageHost;
		this.storageBasepath = storageBasepath;
		this.storageType = storageType;
		this.deadline = deadline;
		this.statementLink = statementLink;
		this.hasTeam = hasTeam;
		this.team = team;
	}

}
