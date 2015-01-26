package ro.pub.cs.vmchecker.client.service.json;

public final class NullDecoder extends JSONDecoder<Boolean> {

	@Override
	protected Boolean decode(String text) {
		return new Boolean(true); 
	}

}
