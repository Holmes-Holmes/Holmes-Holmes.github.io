package xjf;

import org.apache.lucene.analysis.*;
import org.apache.lucene.analysis.miscellaneous.WordDelimiterGraphFilter;
import org.apache.lucene.document.Document;
import org.apache.lucene.document.Field;
import org.apache.lucene.document.TextField;
import org.apache.lucene.queryparser.classic.ParseException;
import org.apache.lucene.queryparser.classic.QueryParser;
import org.apache.lucene.search.Query;
import org.apache.lucene.search.similarities.BM25Similarity;
import org.apache.lucene.search.similarities.Similarity;

import java.io.IOException;

public class JavaPackageMatcher extends CommonPackageMatcher {

    public JavaPackageMatcher(String[] libraryFilePaths) throws IOException {
        super(libraryFilePaths);
    }

    /**
     * Set Similarity Algorithm
     * @return Similarity
     */
    protected Similarity setSimilarity() {
        return new BM25Similarity();
    }

    /**
     * Set Analyzer
     * @return Analyzer
     */
    @Override
    protected Analyzer setAnalyzer() {
        return new JavaPackageAnalyzer();
    }

    /**
     * Set the generation of tmp documents (from vendor and product)
     * @param tmpDoc
     * @param vendor
     * @param product
     */
    @Override
    protected void setTmpDocument(Document tmpDoc, String vendor, String product) {
        super.setTmpDocument(tmpDoc, vendor, product);
    }

    /**
     * Set the generation of documents (from package)
     * @param doc
     * @param pkg
     */
    @Override
    protected void setDocument(Document doc, String pkg) {
        super.setDocument(doc, pkg);
    }

    /**
     * Set Query
     * @param vendor
     * @param product
     * @return Query
     * @throws ParseException
     */
    @Override
    protected Query setQuery(String vendor, String product) throws ParseException {
        if (vendor != null && vendor.contains("pivotal_software")) vendor = "springframework";
        return super.setQuery(vendor, product);
    }
}

/**
 * Java's analyzer
 */
class JavaPackageAnalyzer extends CommonPackageAnalyzer {
    public static final String[] JAVA_PACKAGE_STOP_WORDS = {
            "software", "consulting", "foundation", "project", "framework",
            "linux", "java", "j"
    };

    @Override
    protected TokenStreamComponents createComponents(String s) {
        Tokenizer tokenizer = new LetterAndDigitTokenizer();
        TokenStream stream;
        stream = new RemovingLastNumberFilter(tokenizer);
        stream = new RemovingDomainFilter(stream);
        stream = new WordDelimiterGraphFilter(stream, 0b011100001, null);
        stream = new LowerCaseFilter(stream);
        stream = new StopFilter(stream, makeCharArraySet(JAVA_PACKAGE_STOP_WORDS));
        stream = new DeduplicationFilter(stream);
        return new TokenStreamComponents(tokenizer, stream);
    }
}