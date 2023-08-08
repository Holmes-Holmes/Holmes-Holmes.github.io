package xjf;

import java.io.IOException;
import java.io.FileWriter;

import org.apache.lucene.queryparser.classic.ParseException;

import org.junit.BeforeClass;
import org.junit.Test;


import static org.junit.Assert.assertTrue;

public class FilePathMatcherTest {
    private static CommonFilePathMatcher commonMatcher;

    @BeforeClass
    public static void beforeClass() throws IOException {
        long startTime = System.currentTimeMillis();
        commonMatcher = new CommonFilePathMatcher(new String[] {
                "../../components_data/eco_version_dataset_for_lucene/go_filepath.json",
//                "../../components_data/eco_version_dataset_for_lucene/maven_filepath.json",
//                "../../components_data/eco_version_dataset_for_lucene/npm_filepath.json",
//                "../../components_data/eco_version_dataset_for_lucene/pypi_filepath.json"

        });
        long endTime = System.currentTimeMillis();
        System.out.println("Time cost: " + (endTime - startTime) / 1000.0 + "s.");
    }

    @Test
    public void commonMatcherTest() throws IOException, ParseException {
        oneToOneTest(commonMatcher, "0.0.0", "manpy");
    }

    private boolean oneToOneTest(CommonFilePathMatcher matcher, String filePath, String answer) throws IOException, ParseException {
        String[] results = matcher.search(filePath);
        String query = filePath;
        String filename = String.format("FilePathMatcherTest%s.txt", answer);

        try {
            FileWriter writer = new FileWriter(filename);

            if (results.length < 1) {
                writer.write("X " + query + " ---expect--> " + answer + "\n");
                writer.write("   > ------  --------\n");
                return false;
            }
            boolean success = results[0].split(CommonFilePathMatcher.DELIMITER)[0]
                    .replaceFirst(CommonFilePathMatcher.L1_SPLIT_STR, " ").equals(answer);
            if (success) writer.write("V ");
            else writer.write("X ");
            writer.write(query + " ---expect--> " + answer + "\n");
            for (String result : results) {
                String[] _tmp = result.split(CommonFilePathMatcher.DELIMITER);
                String _language = _tmp[0].replaceFirst(CommonFilePathMatcher.L1_SPLIT_STR, ":");
                String _componentName = _tmp[1];
                String _filePath = _tmp[2];
                String score = String.format("%.4f", Float.parseFloat(_tmp[3]));
                writer.write(String.format("%s > %s | %s  %s%n", _language, _componentName, _filePath, score));
            }
            writer.close();
            System.out.printf("Test complete! You can see the result in %s", filename);
            return success;
        } catch (IOException e) {
            System.out.println("Error: " + e.getMessage());
            return false;
        }
    }
}
