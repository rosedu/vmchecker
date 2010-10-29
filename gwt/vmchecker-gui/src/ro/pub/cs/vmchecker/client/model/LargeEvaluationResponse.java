package ro.pub.cs.vmchecker.client.model;

public class LargeEvaluationResponse {

	public boolean status;
	public String error;

	public LargeEvaluationResponse(boolean status, String error) {
		this.status = status;
		this.error = error;
	}
}
