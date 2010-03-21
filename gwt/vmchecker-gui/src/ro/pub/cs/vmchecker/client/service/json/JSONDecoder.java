package ro.pub.cs.vmchecker.client.service.json;


public interface JSONDecoder<T> {

	T decode(String text) throws Exception; 
}
