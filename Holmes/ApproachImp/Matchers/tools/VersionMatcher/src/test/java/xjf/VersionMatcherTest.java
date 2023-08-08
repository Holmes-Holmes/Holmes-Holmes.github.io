package xjf;

import java.io.IOException;
import java.io.FileWriter;

import org.apache.lucene.queryparser.classic.ParseException;

import org.junit.BeforeClass;
import org.junit.Test;


import static org.junit.Assert.assertTrue;

public class VersionMatcherTest {
    private static CommonVersionMatcher commonMatcher;
    @BeforeClass
    public static void beforeClass() throws IOException {
        long startTime = System.currentTimeMillis();
        commonMatcher = new CommonVersionMatcher(new String[] {
                "../../components_data/eco_version_dataset_for_lucene/go_versions_halved.json",
//                "../../components_data/eco_version_dataset_for_lucene/maven_versions_cleand.json",
//                "../../components_data/eco_version_dataset_for_lucene/npm_versions_cleand.json",
//                "../../components_data/eco_version_dataset_for_lucene/pypi_versions_cleand.json"

        });
        long endTime = System.currentTimeMillis();
        System.out.println("Time cost: " + (endTime - startTime) / 1000.0 + "s.");
    }

    @Test
    public void commonMatcherTest() throws IOException, ParseException {
        oneToOneTest(commonMatcher, "1.0.1 1.0.3 2.0.0 1.0.4 1.2.2 1.1.0 1.2.1 1.2.0", "hilbertcurve");
        oneToOneTest(commonMatcher, "0.11 0.1", "countop");
        oneToOneTest(commonMatcher, "0.4.1 0.7.0 0.3.0 0.5.1 0.2.0 0.6.2 0.7.1 0.6.0 0.5.0 0.6.1 0.8.1 0.8.0", "obspyck");
        oneToOneTest(commonMatcher, "0.0.0", "manpy");
    }

    private boolean oneToOneTest(CommonVersionMatcher matcher, String version, String answer) throws IOException, ParseException {
        String[] results = matcher.search(version);
        String query = version;
        String filename = String.format("VersionMatcherTest%s.txt", answer);

        try {
            FileWriter writer = new FileWriter(filename);

            if (results.length < 1) {
                writer.write("X " + query + " ---expect--> " + answer + "\n");
                writer.write("   > ------  --------\n");
                return false;
            }
            boolean success = results[0].split(CommonVersionMatcher.DELIMITER)[0]
                    .replaceFirst(CommonVersionMatcher.L1_SPLIT_STR, " ").equals(answer);
            if (success) writer.write("V ");
            else writer.write("X ");
            writer.write(query + " ---expect--> " + answer + "\n");
            for (String result : results) {
                String[] _tmp = result.split(CommonVersionMatcher.DELIMITER);
                String _language = _tmp[0].replaceFirst(CommonVersionMatcher.L1_SPLIT_STR, ":");
                String _componentName = _tmp[1];
                String _version = _tmp[2];
                String score = String.format("%.4f", Float.parseFloat(_tmp[3]));
                writer.write(String.format("%s > %s | %s  %s%n", _language, _componentName, _version, score));
            }
            writer.close();
            System.out.println(String.format("Results in: %s", filename));
            return success;
        } catch (IOException e) {
            System.out.println("Error: " + e.getMessage());
            return false;
        }
    }
}
