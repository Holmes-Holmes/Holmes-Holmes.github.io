package xjf;

import org.apache.lucene.analysis.Analyzer;
import org.apache.lucene.document.Document;
import org.apache.lucene.queryparser.classic.ParseException;
import org.apache.lucene.queryparser.classic.QueryParser;
import org.apache.lucene.search.Query;
import org.apache.lucene.search.similarities.Similarity;

import java.io.IOException;

public class PythonPackageMatcher extends CommonPackageMatcher {

    public PythonPackageMatcher(String[] libraryFilePaths) throws IOException {
        super(libraryFilePaths);
    }

    /**
     * Set Similarity Algorithm
     * @return Similarity
     */
    protected Similarity setSimilarity() {
        return new BM25WithoutFreqSimilarity();
    }

    /**
     * Set Analyzer
     * @return Analyzer
     */
    @Override
    protected Analyzer setAnalyzer() {
        return new JavascriptPackageAnalyzer();
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
        if ("moinmo".equals(vendor) && "moinmoin".equals(product)) product = "moin";
        return super.setQuery(vendor, product);
    }
}
