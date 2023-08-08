package xjf;

import java.io.IOException;
import java.io.StringReader;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;

import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.JSONArray;
import org.apache.lucene.analysis.*;
import org.apache.lucene.analysis.core.WhitespaceAnalyzer;
import org.apache.lucene.analysis.miscellaneous.WordDelimiterGraphFilter;
import org.apache.lucene.analysis.tokenattributes.CharTermAttribute;
import org.apache.lucene.analysis.util.CharTokenizer;
import org.apache.lucene.document.Document;
import org.apache.lucene.document.Field;
import org.apache.lucene.document.TextField;
import org.apache.lucene.index.*;
import org.apache.lucene.queryparser.classic.ParseException;
import org.apache.lucene.queryparser.classic.QueryParser;
import org.apache.lucene.search.*;
import org.apache.lucene.search.similarities.Similarity;
import org.apache.lucene.store.ByteBuffersDirectory;
import org.apache.lucene.store.Directory;

public class CommonClassNameMatcher{
    public static final String DELIMITER = "#";
    public static final String L1_SPLIT_STR = "__fdse__";
    protected static final String FIELD_TMP = "tmp";
    protected static final String FIELD_CLASSNAME = "className";
    protected static final String FIELD_LANGUAGE = "language";

    protected static final String FIELD_COMPONENT = "component";

    private final String[] libraryFilePaths;        // 所有的可搜索的第三方构件库
    protected int maxResultCnt = Integer.MAX_VALUE;                 // 返回的最大结果数量

    protected Similarity similarity;
    protected Analyzer analyzer;
    protected IndexWriter writer;
    protected DirectoryReader reader;
    protected IndexSearcher searcher;


    public CommonClassNameMatcher(String[] libraryFilePaths) throws IOException {
        this.libraryFilePaths = libraryFilePaths;
        build();
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
    protected Analyzer setAnalyzer() {
        return new WhitespaceAnalyzer();
    }

    /**
     * Set the generation of tmpDocuments
     * @param tmpDoc
     * @param className
     */
    protected void setTmpDocument(Document tmpDoc, String className) {
        String[] classNames = className.split(" ");
        for (String v : classNames) {
            tmpDoc.add(new TextField(FIELD_CLASSNAME, className, Field.Store.YES));
        }
    }

    /**
     * Set the generation of tmpDocuments
     * @param doc
     * @param className
     */
    protected void setDocument(Document doc, String className) {
        doc.add(new TextField(FIELD_CLASSNAME, className, Field.Store.YES));
    }

    /**
     * Set Query
     * @param className
     * @return Query
     * @throws ParseException
     */
    protected Query setQuery(String className) throws ParseException {
        if (className != null && className.length() == 0) className= null;
        String queryString;
        queryString = String.format("(%s)^%f", className, 1.0);
        return new QueryParser(FIELD_CLASSNAME, analyzer).parse(queryString);
    }

    public final void setMaxResultCnt(int maxResultCnt) { this.maxResultCnt = maxResultCnt; }
    public final int getMaxResultCnt() { return this.maxResultCnt; }

    /**
     * Filter and split words
     * @param doc
     * @return words after filtering and splitting (split by blank space)
     * @throws IOException TokenStream
     */
    public final String filter(String doc) throws IOException {
        StringReader reader = new StringReader(doc);
        TokenStream stream = this.analyzer.tokenStream("", reader);
        CharTermAttribute attribute = stream.addAttribute(CharTermAttribute.class);
        stream.reset();
        StringBuilder filtered = new StringBuilder();
        while(stream.incrementToken()) {
            filtered.append(attribute.toString()).append(' ');
        }
        stream.close();
        return filtered.toString();
    }

    /**
     * Search ClassName
     * @param className
     * @return Results ranked by score, each result has the pattern: "<package><DELIMITER><score>"
     * @throws IOException
     * @throws ParseException
     */
    public final String[] search(String className) throws IOException, ParseException {
        className = preprocessLexical(className);

        Query query = this.setQuery(className);
        ScoreDoc[] hits = this.searcher.search(query, maxResultCnt).scoreDocs;
        String[] results = new String[hits.length];
        for (int i = 0; i < hits.length; ++i) {
            ScoreDoc hit = hits[i];
            Document hitDoc = this.searcher.doc(hit.doc);
            results[i] = hitDoc.get(FIELD_LANGUAGE) + DELIMITER + hitDoc.get(FIELD_COMPONENT) + DELIMITER + hitDoc.get(FIELD_CLASSNAME) + DELIMITER + hit.score;
            if (hitDoc.get(FIELD_TMP) != null) {
                String tmp = results[i];
                results[i] = results[0];
                results[0] = tmp;
            }
        }
        return results;
    }

    /**
     * Get the first word in a certain string
     * @param str
     * @return the first word in the string or null
     */
    protected String getFirstWord(String str) {
        String[] split = str.split("[_\\-/0-9]");
        for (String s : split) {
            if (s.length() != 0) return s;
        }
        return null;
    }

    /**
     * Bulid Lucene
     * @throws IOException
     */
    private void build() throws IOException {
        this.similarity = this.setSimilarity();
        this.analyzer = this.setAnalyzer();

        Directory directory = new ByteBuffersDirectory();
        this.writer = new IndexWriter(directory, new IndexWriterConfig(this.analyzer));

        for (String libraryFilePath : libraryFilePaths) {
            String[] _split = libraryFilePath.split("[/\\\\]");
            String _name = _split[_split.length - 1].toLowerCase();
            _name = _name.substring(0, _name.lastIndexOf("."));

            String language;
            if (_name.contains("java") || _name.contains("maven")){
                language = "java";
            }
            else if (_name.contains("javascript") || _name.contains("npm") || _name.contains("js")){
                language = "javascript";
            }
            else if (_name.contains("python") || _name.contains("pypi")) {
                language = "python";
            }
            else if (_name.contains("go")) {
                language = "go";
            }
            else language = "unknown";

            List<String> lines = Files.readAllLines(Paths.get(libraryFilePath));
            StringBuilder stringBuilder = new StringBuilder();
            for (String line : lines)  {
                stringBuilder.append(line);
            }
            String jsonString = stringBuilder.toString();
            JSONArray array = JSON.parseArray(jsonString);

            for (Object obj : array) {
                String classNames = ((String) obj);
                String componentName = classNames.substring(0, classNames.indexOf(L1_SPLIT_STR));
                String version = classNames.substring(classNames.indexOf(L1_SPLIT_STR) + L1_SPLIT_STR.length(), classNames.length());
                classNames = version.replace(L1_SPLIT_STR, " ");
                Document doc = new Document();
                doc.add(new TextField(FIELD_LANGUAGE, language, Field.Store.YES));
                doc.add(new TextField(FIELD_COMPONENT, componentName, Field.Store.YES));
                this.setDocument(doc, classNames);
                this.writer.addDocument(doc);
            }
        }
        this.writer.commit();

        this.reader = DirectoryReader.open(directory);
        this.searcher = new IndexSearcher(this.reader);
        this.searcher.setSimilarity(similarity);
    }

    /**
     * Remove illegal letters in text
     * @param text
     * @return processed text
     */
    private String preprocessLexical(String text) {
        if (text == null) return null;
        return text.replaceAll("[\\\\/?`~!@#$%^&*=+|]", " ");
    }

    /**
     * Remove illegal letters in text
     * @param text
     * @return processed text
     */
    private String detailPreprocessLexical(String text) {
        if (text == null) return null;
        return text.replaceAll("[\\\\/?`~!@#$%^&*=+|.:-]", " ");
    }

    /**
     * Get IndexSearcher
     * @throws IOException
     */
    private void updateSearcher() throws IOException {
        DirectoryReader newReader = DirectoryReader.openIfChanged(this.reader, this.writer);
        if (newReader != null) {
            this.reader.close();
            this.reader = newReader;
            this.searcher = new IndexSearcher(this.reader);
            this.searcher.setSimilarity(similarity);
        }
    }
}
