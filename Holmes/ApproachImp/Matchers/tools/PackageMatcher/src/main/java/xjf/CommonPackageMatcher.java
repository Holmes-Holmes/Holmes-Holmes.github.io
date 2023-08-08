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


public class CommonPackageMatcher {
    public static final String DELIMITER = "#";
    public static final String L1_SPLIT_STR = "__fdse__";
    protected static final String FIELD_PACKAGE = "package";
    protected static final String FIELD_LANGUAGE = "language";

    private final String[] libraryFilePaths;
    protected int maxResultCnt = Integer.MAX_VALUE;

    protected Similarity similarity;
    protected Analyzer analyzer;
    protected IndexWriter writer;
    protected DirectoryReader reader;
    protected IndexSearcher searcher;


    public CommonPackageMatcher(String[] libraryFilePaths) throws IOException {
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
        return new CommonPackageAnalyzer();
    }

    /**
     * Set the generation of tmp documents (from vendor and product)
     * @param tmpDoc
     * @param vendor
     * @param product
     */
    protected void setTmpDocument(Document tmpDoc, String vendor, String product) {
        String name = vendor + ":" + product;
        tmpDoc.add(new TextField(FIELD_PACKAGE, name, Field.Store.YES));
    }

    /**
     * Set the generation of documents (from package)
     * @param doc
     * @param pkg
     */
    protected void setDocument(Document doc, String pkg) {
        doc.add(new TextField(FIELD_PACKAGE, pkg, Field.Store.YES));
    }

    /**
     * Set Query
     * @param vendor
     * @param product
     * @return Query
     * @throws ParseException
     */
    protected Query setQuery(String vendor, String product) throws ParseException {
        if (vendor != null && vendor.length() == 0) vendor = null;
        if (product != null && product.length() == 0) product = null;
        String queryString;
        if (vendor == null || vendor.equals("null")) {
            queryString = product;
        }
        else {
            queryString = String.format("(%s)^%f (%s)^%f", product, 1.5, vendor,0.5);
        }
        return new QueryParser(FIELD_PACKAGE, analyzer).parse(queryString);
    }

    public final void setMaxResultCnt(int maxResultCnt) { this.maxResultCnt = maxResultCnt; }
    public final int getMaxResultCnt() { return this.maxResultCnt; }

    /**
     * Filter and split words
     * @param doc
     * @return words after filtering and splitting (split by blank space)
     * @throws IOException TokenStream IO
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
     * Search Package
     * We search vendor and product separately.
     * @param vendor
     * @param product
     * @return Results ranked by score, each result has the pattern: "<package><DELIMITER><score>"
     * @throws IOException
     * @throws ParseException
     */
    public final String[] search(String vendor, String product) throws IOException, ParseException {
        vendor = preprocessLexical(vendor);
        product = preprocessLexical(product);

        Query query = this.setQuery(vendor, product);
        ScoreDoc[] hits = this.searcher.search(query, maxResultCnt).scoreDocs;
        String[] results = new String[hits.length];
        for (int i = 0; i < hits.length; ++i) {
            ScoreDoc hit = hits[i];
            Document hitDoc = this.searcher.doc(hit.doc);
            results[i] = hitDoc.get(FIELD_LANGUAGE) + DELIMITER + hitDoc.get(FIELD_PACKAGE) + DELIMITER + hit.score;
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
            if (_name.contains(".")) {
                _name = _name.substring(0, _name.lastIndexOf("."));
            }

            String language;
            if (_name.contains("java") || _name.contains("maven")) {
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
            for (String line : lines) stringBuilder.append(line);
            String jsonString = stringBuilder.toString();
            JSONArray array = JSON.parseArray(jsonString);

            for (Object obj : array) {
                String pkg = ((String) obj).replaceAll(L1_SPLIT_STR, ":");
                Document doc = new Document();
                doc.add(new TextField(FIELD_LANGUAGE, language, Field.Store.YES));
                this.setDocument(doc, pkg);
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

/**
 * Analyzer
 * Rules:
 *  1. Split the library name into tokens based on punctuation (“.”, “-”, “_”);
 *  2. Split the library name based on Camel Case;
 *  3. Remove all numbers;
 *  4. Convert all letters to lowercase;
 *  5. Remove duplicate occurrences of words.
 */
class CommonPackageAnalyzer extends Analyzer {
    public CommonPackageAnalyzer() {}

    @Override
    protected TokenStreamComponents createComponents(String s) {
        Tokenizer tokenizer = new LetterAndDigitTokenizer();
        TokenStream stream;
        stream = new RemovingNumberFilter(tokenizer);
        stream = new RemovingDomainFilter(stream);
        stream = new WordDelimiterGraphFilter(stream, 0b011100001, null);
        stream = new LowerCaseFilter(stream);
        stream = new DeduplicationFilter(stream);
        return new TokenStreamComponents(tokenizer, stream);
    }


    /**
     * Get all separators
     * @return all separators
     */
    protected static CharArraySet makeCharArraySet(String[] words) {
        return StopFilter.makeStopSet(words, true);
    }

    /**
     * Tokenizer that removes all punctuation except letters and numbers
     */
    public static final class LetterAndDigitTokenizer extends CharTokenizer {
        @Override
        protected boolean isTokenChar(int c) {
            return Character.isLetter(c) || Character.isDigit(c);
        }
    }

    /**
     * The Domain Removal Filter
     * Remove domain names and subdomains starting with "Package". For example, "au.org".
     */
    public static final class RemovingDomainFilter extends FilteringTokenFilter {
        public static final String[] PACKAGE_DOMAIN_WORDS = {
                "com", "org", "gov", "ac", "net", "www", "io", "xyz", "info", "me", "edu", "int", "top",
                "ai", "at", "au", "be", "br", "cc", "ch", "cn", "co", "cz", "de", "dk", "es", "eu", "fi",
                "fr", "hu", "in", "it", "jp", "kr", "nl", "no", "nz", "pl", "ru", "se", "uk", "github"
        };

        private final CharTermAttribute termAttribute = this.addAttribute(CharTermAttribute.class);
        private final CharArraySet domainWords;
        private boolean firstWord;

        public RemovingDomainFilter(TokenStream in) {
            super(in);
            this.domainWords = makeCharArraySet(PACKAGE_DOMAIN_WORDS);
            this.firstWord = true;
        }

        @Override
        protected boolean accept() {
            boolean hit = this.firstWord
                    && this.domainWords.contains(this.termAttribute.buffer(), 0, this.termAttribute.length());
            this.firstWord = hit;
            return !hit;
        }

        @Override
        public void reset() throws IOException {
            super.reset();
            this.firstWord = true;
        }
    }

    /**
     * The Adjacent Word Pairing Filter
     */
    public static final class ConcatenatingPairFilter extends TokenFilter {
        private final CharTermAttribute termAttribute = this.addAttribute(CharTermAttribute.class);
        private String previousWord = null;
        private boolean addSingleWord = true;

        protected ConcatenatingPairFilter(TokenStream input) {
            super(input);
        }

        @Override
        public boolean incrementToken() throws IOException {
            if (this.addSingleWord && this.previousWord != null) {
                this.addSingleWord = false;
                this.clearAttributes();
                this.termAttribute.append(this.previousWord);
                return true;
            }
            if (this.input.incrementToken()) {
                String word = new String(this.termAttribute.buffer(), 0, this.termAttribute.length());
                if (word.isEmpty()) return true;
                this.clearAttributes();
                if (this.addSingleWord) this.termAttribute.append(word);
                else this.termAttribute.append(this.previousWord).append(word);
                this.previousWord = word;
                this.addSingleWord = !this.addSingleWord;
                return true;
            }
            return false;
        }

        @Override
        public void reset() throws IOException {
            super.reset();
            this.previousWord = null;
            this.addSingleWord = true;
        }
    }

    /**
     * The Filter to Remove Isolated Numbers
     * For example, "abc123def456 111 222" -> "abc123def456".
     */
    public static final class RemovingNumberFilter extends TokenFilter {
        private final CharTermAttribute termAttribute = this.addAttribute(CharTermAttribute.class);

        protected RemovingNumberFilter(TokenStream input) {
            super(input);
        }

        @Override
        public boolean incrementToken() throws IOException {
            while (this.input.incrementToken()) {
                char[] term = this.termAttribute.buffer();
                int length = this.termAttribute.length();
                for (int i = 0; i < length; ++i) {
                    if (!Character.isDigit(term[i])) return true;
                }
            }
            return false;
        }
    }

    /**
     * The Filter to Remove Isolated Numbers at the End
     * For example, "abc 123 def 456 789" -> "abc 123 def".
     */
    public static final class RemovingLastNumberFilter extends TokenFilter {
        private final CharTermAttribute termAttribute = this.addAttribute(CharTermAttribute.class);
        private List<String> noLastNumber = null;
        private int index = 0;

        protected RemovingLastNumberFilter(TokenStream input) {
            super(input);
        }

        @Override
        public boolean incrementToken() throws IOException {
            if (this.noLastNumber == null) {
                this.noLastNumber = new ArrayList<>();
                while (this.input.incrementToken()) {
                    String w = new String(this.termAttribute.buffer(), 0, this.termAttribute.length());
                    this.noLastNumber.add(w);
                }
                while (true) {
                    if (this.noLastNumber.size() == 0) break;
                    String w = this.noLastNumber.get(this.noLastNumber.size() - 1);
                    boolean isNum = true;
                    for (char c : w.toCharArray()) {
                        if (Character.isDigit(c)) continue;
                        isNum = false;
                        break;
                    }
                    if (isNum) this.noLastNumber.remove(this.noLastNumber.size() - 1);
                    else break;
                }
                this.index = 0;
            }
            if (this.index >= this.noLastNumber.size()) return false;
            this.clearAttributes();
            this.termAttribute.append(this.noLastNumber.get(this.index));
            ++this.index;
            return true;
        }

        @Override
        public void reset() throws IOException {
            super.reset();
            this.noLastNumber = null;
            this.index = 0;
        }
    }

    /**
     * The Filter to Remove Duplicate Words in a Sentence
     * For example, "abc def abc def def" -> "abc def"
     */
    public static final class DeduplicationFilter extends TokenFilter {
        private final CharTermAttribute termAttribute = this.addAttribute(CharTermAttribute.class);
        private final CharArraySet previous = new CharArraySet(8, false);

        protected DeduplicationFilter(TokenStream input) {
            super(input);
        }

        @Override
        public boolean incrementToken() throws IOException {
            while (this.input.incrementToken()) {
                char[] term = this.termAttribute.buffer();
                int length = this.termAttribute.length();
                if (this.previous.contains(term, 0, length)) continue;
                char[] saved = new char[length];
                System.arraycopy(term, 0, saved, 0, length);
                this.previous.add(saved);
                return true;
            }
            return false;
        }

        @Override
        public void reset() throws IOException {
            super.reset();
            this.previous.clear();
        }
    }

    /**
     * The Filter to Standardize CPE and Package Version Naming
     */
    public static final class UnifyingVersionNameFilter extends TokenFilter {
        private final CharTermAttribute termAttribute = this.addAttribute(CharTermAttribute.class);

        protected UnifyingVersionNameFilter(TokenStream input) {
            super(input);
        }

        @Override
        public boolean incrementToken() throws IOException {
            if (!this.input.incrementToken()) return false;
            String version = new String(this.termAttribute.buffer(), 0, this.termAttribute.length());
            if (Character.isLetter(version.charAt(0))) return true;
            version = version.replaceFirst("[^0-9]?[A-Za-z].*", "");
            int end = version.length();
            while (end >= 2 && version.charAt(end - 2) == '.' && version.charAt(end - 1) == '0') end -= 2;
            version = version.substring(0, end);
            this.termAttribute.setEmpty();
            this.termAttribute.append(version);
            return true;
        }
    }
}