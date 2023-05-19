import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;

public class Example {
	
	private File aFile;
	private InputStream aStream;
	private int[][] anArray;
	
	// Constructor
	public Example(String aFileName) {
		this.aFile = new File (aFileName);
		
		int size;
		try {
			this.aStream = new FileInputStream (this.aFile);
			while (this.aStream.available() != 0) {
				this.aStream.read();
				size++;
			}
			
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		
		this.anArray = new int[3][size];
	}

	// Main
	public static void main (String[] args) {
		
		Example Instance = new Example(args[2]);
		System.out.println ("Hello wrom Example...");
	}

	@Override
	public void finalize() {
		try {
			this.aStream.close();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}	
}
