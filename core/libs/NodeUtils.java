package nodeutils;

import java.util.*;
import java.io.*;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.ParserConfigurationException;
import javax.xml.xpath.*;

import org.w3c.dom.Document;
import org.w3c.dom.NodeList;
import org.w3c.dom.Node;
import org.w3c.dom.Element;
import org.xml.sax.SAXException;

import java.io.File;

public class NodeUtils {
	private String xmlFile = "/home/bouli/android-monkey/dump.xml";
	private Node root = null;
	
	public NodeUtils(String file) {
		setXmlFile(file);
		System.out.println("...");
	}
	
	public void say() {
		System.out.println("This is NodeUtils...");
	}
	/*
	 * 
	 */
	public NodeList readXML(String file) throws ParserConfigurationException, SAXException, IOException {
		File xmlFile = new File(file);
		NodeList nList = null;
		DocumentBuilder dBuilder = DocumentBuilderFactory.newInstance().newDocumentBuilder();
		Document doc = dBuilder.parse(xmlFile);
		nList = doc.getElementsByTagName("node");
		return nList;
	}

	/* 
	 * This method is used to find all Nodes.
	 */
	public NodeList findall(Document doc, String xpathExpr) throws XPathExpressionException {
		XPathFactory xPathFactory = XPathFactory.newInstance();
		XPath xpath = xPathFactory.newXPath();
		XPathExpression expr = xpath.compile(xpathExpr);
		NodeList nl = (NodeList) expr.evaluate(doc, XPathConstants.NODESET);
		return nl;
	}
	
	/*
	 * This method is used to get attribute.
	 */
	public String getAttribute(Node nNode, String name) {
		Element eElement = (Element) nNode;
		String attr = eElement.getAttribute(name);
		if (attr != null) {
			return attr;
		}
		else {
			return null;
		}
	}

	public String getXmlFile() {
		return xmlFile;
	}

	public void setXmlFile(String xmlFile) {
		this.xmlFile = xmlFile;
	}
}