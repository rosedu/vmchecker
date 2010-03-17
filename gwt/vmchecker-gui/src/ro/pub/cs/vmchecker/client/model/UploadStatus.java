package ro.pub.cs.vmchecker.client.model;

public class UploadStatus {
	public boolean status; 
	public String dumpLog; 
	
	public UploadStatus(boolean status, String dumpLog) {
		this.status = status; 
		this.dumpLog = dumpLog; 
	}
}
