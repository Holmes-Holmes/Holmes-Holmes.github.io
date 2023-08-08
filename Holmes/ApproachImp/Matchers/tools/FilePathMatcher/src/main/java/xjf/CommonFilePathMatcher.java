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

public class CommonFilePathMatcher {
    public static final String DELIMITER = "#";
    public static final String L1_SPLIT_STR = "__fdse__";
    protected static final String FIELD_TMP = "tmp";
    protected static final String FIELD_FILEPATH = "filePath";
    protected static final String FIELD_LANGUAGE = "language";

    protected static final String FIELD_COMPONENT = "component";

    private final String[] libraryFilePaths;
    protected int maxResultCnt = Integer.MAX_VALUE;

    protected Similarity similarity;
    protected Analyzer analyzer;
    protected IndexWriter writer;
    protected DirectoryReader reader;
    protected IndexSearcher searcher;

    public CommonFilePathMatcher(String[] libraryFilePaths) throws IOException {
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
     * Set the generation of tmp documents (from filepaths)
     * @param tmpDoc
     * @param filePath
     */
    protected void setTmpDocument(Document tmpDoc, String filePath) {
        String[] filePaths = filePath.split(" ");
        for (String fp : filePaths) {
            tmpDoc.add(new TextField(FIELD_FILEPATH, fp, Field.Store.YES));
        }
    }

    /**
     * Set the generation of documents (from filepaths)
     * @param doc
     * @param filePath
     */
    protected void setDocument(Document doc, String filePath) {
        doc.add(new TextField(FIELD_FILEPATH, filePath, Field.Store.YES));
    }

    /**
     * Set query
     * @param filePath
     * @return Query
     * @throws ParseException
     */
    protected Query setQuery(String filePath) throws ParseException {
        if (filePath != null && filePath.length() == 0) filePath= null;
        String queryString;
        queryString = String.format("(%s)^%f", filePath, 1.0);
        return new QueryParser(FIELD_FILEPATH, analyzer).parse(queryString);
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
     * Search FilePath
     * @param filePath
     * @return Results ranked by score, each result has the pattern: "<package><DELIMITER><score>"
     * @throws IOException
     * @throws ParseException
     */
    public final String[] search(String filePath) throws IOException, ParseException {
        filePath = preprocessLexical(filePath);

        Query query = this.setQuery(filePath);
        ScoreDoc[] hits = this.searcher.search(query, maxResultCnt).scoreDocs;
        String[] results = new String[hits.length];
        for (int i = 0; i < hits.length; ++i) {
            ScoreDoc hit = hits[i];
            Document hitDoc = this.searcher.doc(hit.doc);
            results[i] = hitDoc.get(FIELD_LANGUAGE) + DELIMITER + hitDoc.get(FIELD_COMPONENT) + DELIMITER + hitDoc.get(FIELD_FILEPATH) + DELIMITER + hit.score;
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
                String filePaths = ((String) obj);
                String componentName = filePaths.substring(0, filePaths.indexOf(L1_SPLIT_STR));
                String filePath = filePaths.substring(filePaths.indexOf(L1_SPLIT_STR) + L1_SPLIT_STR.length(), filePaths.length());
                filePaths = filePath.replace(L1_SPLIT_STR, " ");
                Document doc = new Document();
                doc.add(new TextField(FIELD_LANGUAGE, language, Field.Store.YES));
                doc.add(new TextField(FIELD_COMPONENT, componentName, Field.Store.YES));
                this.setDocument(doc, filePaths);
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
