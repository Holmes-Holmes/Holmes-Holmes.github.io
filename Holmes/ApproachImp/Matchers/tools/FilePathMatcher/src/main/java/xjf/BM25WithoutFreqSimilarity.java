package xjf;

import java.util.ArrayList;
import java.util.List;

import org.apache.lucene.index.FieldInvertState;
import org.apache.lucene.index.IndexOptions;
import org.apache.lucene.search.CollectionStatistics;
import org.apache.lucene.search.Explanation;
import org.apache.lucene.search.TermStatistics;
import org.apache.lucene.search.similarities.Similarity;
import org.apache.lucene.util.BytesRef;
import org.apache.lucene.util.SmallFloat;


public class BM25WithoutFreqSimilarity extends Similarity {
    private final float k1;
    private final float b;

    public BM25WithoutFreqSimilarity(float k1, float b) {
        if (!Float.isFinite(k1) || k1 < 0) {
            throw new IllegalArgumentException("illegal k1 value: " + k1 + ", must be a non-negative finite value");
        }
        if (Float.isNaN(b) || b < 0 || b > 1) {
            throw new IllegalArgumentException("illegal b value: " + b + ", must be between 0 and 1");
        }
        this.k1 = k1;
        this.b  = b;
    }

    public BM25WithoutFreqSimilarity() {
        this(1.2f, 0.75f);
    }

    /**
     * Calculate Term Frequency
     * @param docFreq
     * @return 0 or 1
     */
    protected static long tf(long docFreq) {
        return docFreq > 0 ? 1 : 0;
    }

    /**
     * Calculate Term Frequency
     * @param docFreq
     * @return 0.0 or 1.0
     */
    protected static float tf(float docFreq) {
        return docFreq > 1e-6f ? 1f : 0f;
    }

    protected float idf(long docFreq, long docCount) {
        return (float) Math.log(1 + (docCount - tf(docFreq) + 0.5D)/(tf(docFreq) + 0.5D));
    }

    protected float scorePayload(int doc, int start, int end, BytesRef payload) {
        return 1;
    }

    protected float avgFieldLength(CollectionStatistics collectionStats) {
        return (float) (collectionStats.sumTotalTermFreq() / (double) collectionStats.docCount());
    }

    protected boolean discountOverlaps = true;

    public void setDiscountOverlaps(boolean v) {
        discountOverlaps = v;
    }

    public boolean getDiscountOverlaps() {
        return discountOverlaps;
    }

    private static final float[] LENGTH_TABLE = new float[256];

    static {
        for (int i = 0; i < 256; i++) {
            LENGTH_TABLE[i] = SmallFloat.byte4ToInt((byte) i);
        }
    }

    @Override
    public final long computeNorm(FieldInvertState state) {
        final int numTerms;
        if (state.getIndexOptions() == IndexOptions.DOCS && state.getIndexCreatedVersionMajor() >= 8) {
            numTerms = state.getUniqueTermCount();
        } else if (discountOverlaps) {
            numTerms = state.getLength() - state.getNumOverlap();
        } else {
            numTerms = state.getLength();
        }
        return SmallFloat.intToByte4(numTerms);
    }

    public Explanation idfExplain(CollectionStatistics collectionStats, TermStatistics termStats) {
        final long df = termStats.docFreq();
        final long docCount = collectionStats.docCount();
        final float idf = idf(df, docCount);
        return Explanation.match(idf, "idf, computed as log(1 + (N - n + 0.5) / (n + 0.5)) from:",
                Explanation.match(df, "n, number of documents containing term"),
                Explanation.match(docCount, "N, total number of documents with field"));
    }

    public Explanation idfExplain(CollectionStatistics collectionStats, TermStatistics[] termStats) {
        double idf = 0d;
        List<Explanation> details = new ArrayList<>();
        for (final TermStatistics stat : termStats ) {
            Explanation idfExplain = idfExplain(collectionStats, stat);
            details.add(idfExplain);
            idf += idfExplain.getValue().floatValue();
        }
        return Explanation.match((float) idf, "idf, sum of:", details);
    }

    @Override
    public SimScorer scorer(float boost, CollectionStatistics collectionStats, TermStatistics... termStats) {
        Explanation idf = termStats.length == 1 ? idfExplain(collectionStats, termStats[0]) : idfExplain(collectionStats, termStats);
        float avgdl = avgFieldLength(collectionStats);

        float[] cache = new float[256];
        for (int i = 0; i < cache.length; i++) {
            cache[i] = 1f / (k1 * ((1 - b) + b * LENGTH_TABLE[i] / avgdl));
        }
        return new BM25WithoutFreqScorer(boost, k1, b, idf, avgdl, cache);
    }

    protected static class BM25WithoutFreqScorer extends SimScorer {
        /** query boost */
        private final float boost;
        /** k1 value for scale factor */
        private final float k1;
        /** b value for length normalization impact */
        private final float b;
        /** BM25's idf */
        private final Explanation idf;
        /** The average document length. */
        private final float avgdl;
        /** precomputed norm[256] with k1 * ((1 - b) + b * dl / avgdl) */
        private final float[] cache;
        /** weight (idf * boost) */
        private final float weight;

        BM25WithoutFreqScorer(float boost, float k1, float b, Explanation idf, float avgdl, float[] cache) {
            this.boost = boost;
            this.idf = idf;
            this.avgdl = avgdl;
            this.k1 = k1;
            this.b = b;
            this.cache = cache;
            this.weight = boost * idf.getValue().floatValue();
        }

        @Override
        public float score(float freq, long encodedNorm) {
            float normInverse = cache[((byte) encodedNorm) & 0xFF];
            return weight - weight / (1f + tf(freq) * normInverse);
        }

        @Override
        public Explanation explain(Explanation freq, long encodedNorm) {
            List<Explanation> subs = new ArrayList<>(explainConstantFactors());
            Explanation tfExpl = explainTF(freq, encodedNorm);
            subs.add(tfExpl);
            float normInverse = cache[((byte) encodedNorm) & 0xFF];
            return Explanation.match(weight - weight / (1f + freq.getValue().floatValue() * normInverse),
                    "score(freq="+freq.getValue()+"), computed as boost * idf * tf from:", subs);
        }

        private Explanation explainTF(Explanation freq, long norm) {
            List<Explanation> subs = new ArrayList<>();
            subs.add(freq);
            subs.add(Explanation.match(k1, "k1, term saturation parameter"));
            float doclen = LENGTH_TABLE[((byte) norm) & 0xff];
            subs.add(Explanation.match(b, "b, length normalization parameter"));
            if ((norm & 0xFF) > 39) {
                subs.add(Explanation.match(doclen, "dl, length of field (approximate)"));
            } else {
                subs.add(Explanation.match(doclen, "dl, length of field"));
            }
            subs.add(Explanation.match(avgdl, "avgdl, average length of field"));
            float normInverse = 1f / (k1 * ((1 - b) + b * doclen / avgdl));
            return Explanation.match(
                    1f - 1f / (1 + freq.getValue().floatValue() * normInverse),
                    "tf, computed as freq / (freq + k1 * (1 - b + b * dl / avgdl)) from:", subs);
        }

        private List<Explanation> explainConstantFactors() {
            List<Explanation> subs = new ArrayList<>();
            // query boost
            if (boost != 1.0f) {
                subs.add(Explanation.match(boost, "boost"));
            }
            // idf
            subs.add(idf);
            return subs;
        }
    }

    @Override
    public String toString() {
        return "BM25(k1=" + k1 + ",b=" + b + ")";
    }

    public final float getK1() {
        return k1;
    }

    public final float getB() {
        return b;
    }
}
