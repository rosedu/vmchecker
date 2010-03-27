package ro.pub.cs.vmchecker.client.model;

public class EvaluationResult {

	public String step; 
	public String dump; 
	
	public EvaluationResult(String step, String dump) {
		this.step = step; 
		this.dump = dump; 
	}
	
	public String toHTML() {
		String resultHTML; 
		resultHTML = "<b>" + step + "</b><br/>";
		resultHTML += "<pre>" + dump + "</pre><hr/>"; 
		return resultHTML; 
	}
}
