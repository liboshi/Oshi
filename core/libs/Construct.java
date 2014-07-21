package nodeutils;

import java.io.IOException;

import javax.xml.parsers.ParserConfigurationException;

import org.xml.sax.SAXException;

import nodeutils.NodeUtils;

public class Construct {
	public static void main(String[] args) throws ParserConfigurationException, SAXException {
		NodeUtils nu = new NodeUtils("/home/bouli/android-monkey/window_dump.xml");
		nu.say();
		try {
			nu.readXML("/home/bouli/android-monkey/window_dump.xml");
		} catch (IOException ioError) {
			System.err.println("IO Exception: " + ioError);
		}
		//nu.setXmlFile("liboshi");
		System.out.println(nu.getXmlFile());
	}
}
