package ro.pub.cs.vmchecker.client.model;

public class Md5Status {
	public boolean fileExists;
	public String md5Sum;
	public String uploadTime;

	public Md5Status(boolean fileExists, String md5Sum, String uploadTime) {
		this.fileExists = fileExists;
		this.md5Sum = md5Sum;
		this.uploadTime = uploadTime;
	}
}
