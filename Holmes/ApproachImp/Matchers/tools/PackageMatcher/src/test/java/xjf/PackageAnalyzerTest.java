package xjf;

import org.apache.lucene.analysis.Analyzer;
import org.apache.lucene.analysis.TokenStream;
import org.apache.lucene.analysis.core.SimpleAnalyzer;
import org.apache.lucene.analysis.standard.StandardAnalyzer;
import org.apache.lucene.analysis.tokenattributes.CharTermAttribute;
import org.junit.Test;
import org.owasp.dependencycheck.data.lucene.SearchFieldAnalyzer;

import java.io.IOException;
import java.io.StringReader;


public class PackageAnalyzerTest {
    @Test
    public void analyzersTest() throws IOException, IllegalAccessException, InstantiationException {
        String str = "Nick's this it is a an analyzersTest/j.python,Javascript-Go@c++ C# 1-0 int32char8bit1 apples 222 1234";
        analyzerTest(new SimpleAnalyzer(), str);
        analyzerTest(new StandardAnalyzer(), str);
        analyzerTest(new SearchFieldAnalyzer(), str);
        analyzerTest(new CommonPackageAnalyzer(), str);
        analyzerTest(new JavaPackageAnalyzer(), str);
        analyzerTest(new JavascriptPackageAnalyzer(), str);
        Class<?>[] analyzerClasses = {
                CommonPackageAnalyzer.class, JavaPackageAnalyzer.class, JavascriptPackageAnalyzer.class
        };
        for (Class<?> analyzerClass : analyzerClasses) {
            CommonPackageAnalyzer analyzer = (CommonPackageAnalyzer) analyzerClass.newInstance();
            analyzerTest(analyzer, "haha jquery-jquery nick nick nick an jQuery apples");
            analyzerTest(analyzer, "AbcdEFghIJKlMnOP __fdse__xerces2_java");
            analyzerTest(analyzer, "[+\\-&|!()_{}\\[\\]\"~*?:\\\\/<>,;']+");
            analyzerTest(analyzer, "node.inc.js");
            analyzerTest(analyzer, "net.test:asdfasf.net");
            analyzerTest(analyzer, "aaa net.test:asdfasf.net");
            analyzerTest(analyzer, "aaa bbb net.test:asdfasf.net");
            analyzerTest(analyzer, "org.net.net.ac.www.ac.ac.xyz.asdfasf.net.io");
            analyzerTest(analyzer, "abc123xyz456 0ha1ha ijk-6.11.3");
            analyzerTest(analyzer, "apache__fdse__xerces2_java");
            analyzerTest(analyzer, "xerces__fdse__xercesImpl");
            analyzerTest(analyzer, "com.rackspace.apache__fdse__xerces2-xsd11");
            analyzerTest(analyzer, "org.kie.modules__fdse__org-apache-xerces-main");
            analyzerTest(analyzer, "github.com:tidwall__fdse__gjson");
            analyzerTest(analyzer, "mule__fdse__mule-email-provider__fdse__1.0");
        }
    }

    @Test
    public void commonAnalyzerTest() throws IOException {
        Analyzer analyzer = new CommonPackageAnalyzer();
        analyzerTest(analyzer, "xerces2_java");
        analyzerTest(analyzer, "xercesImpl-123-456");
    }

    @Test
    public void javascriptAnalyzerTest() throws IOException {
        Analyzer analyzer = new JavascriptPackageAnalyzer();
        analyzerTest(analyzer, "11xiaoli");
        analyzerTest(analyzer, "apk-parser3");
    }

    @Test
    public void javaAnalyzerTest() throws IOException {
        Analyzer analyzer = new JavaPackageAnalyzer();
        analyzerTest(analyzer, "www aaa bbb 11 aa 22");
        analyzerTest(analyzer, "www aaa bbb 13 31 aa 22");
        analyzerTest(analyzer, "www aaa bbb 11 aa 22 33");
        analyzerTest(analyzer, "apk-1.0--parser3 44 44 434");
    }

    private void analyzerTest(Analyzer analyzer, String str) throws IOException {
        System.out.print(analyzer.getClass().getSimpleName() + ": ");
        StringReader reader = new StringReader(str);
        TokenStream stream = analyzer.tokenStream("", reader);
        CharTermAttribute attribute = stream.addAttribute(CharTermAttribute.class);
        stream.reset();
        while(stream.incrementToken()) {
            System.out.print(attribute + ", ");
        }
        System.out.println();
        stream.close();
    }
}
