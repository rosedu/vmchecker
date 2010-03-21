package ro.pub.cs.vmchecker.client.service.json;

public class NullDecoder implements JSONDecoder<Boolean> {

	@Override
	public Boolean decode(String text) throws Exception {
		return new Boolean(true); 
	}

}
