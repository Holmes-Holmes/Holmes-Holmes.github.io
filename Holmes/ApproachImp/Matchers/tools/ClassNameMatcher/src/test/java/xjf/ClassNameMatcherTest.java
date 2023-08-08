package xjf;

import java.io.IOException;
import java.io.FileWriter;

import org.apache.lucene.queryparser.classic.ParseException;

import org.junit.BeforeClass;
import org.junit.Test;


import static org.junit.Assert.assertTrue;

public class ClassNameMatcherTest {
    private static CommonClassNameMatcher commonMatcher;
    @BeforeClass
    public static void beforeClass() throws IOException {
        long startTime = System.currentTimeMillis();
        commonMatcher = new CommonClassNameMatcher(new String[] {
                "../../components_data/eco_version_dataset_for_lucene/go_classname.json",
//                "../../components_data/eco_version_dataset_for_lucene/maven_classname.json",
//                "../../components_data/eco_version_dataset_for_lucene/npm_classname.json",
//                "../../components_data/eco_version_dataset_for_lucene/pypi_classname.json"

        });
        long endTime = System.currentTimeMillis();
        System.out.println("Time cost: " + (endTime - startTime) / 1000.0 + "s.");
    }

    @Test
    public void commonMatcherTest() throws IOException, ParseException {
        oneToOneTest(commonMatcher, "netty", "netty.io");
    }

    private boolean oneToOneTest(CommonClassNameMatcher matcher, String className, String answer) throws IOException, ParseException {
        String[] results = matcher.search(className);
        String query = className;
        String filename = String.format("VersionMatcherTest%s.txt", answer);

        try {
            FileWriter writer = new FileWriter(filename);

            if (results.length < 1) {
                writer.write("X " + query + " ---expect--> " + answer + "\n");
                writer.write("   > ------  --------\n");
                return false;
            }
            boolean success = results[0].split(CommonClassNameMatcher.DELIMITER)[0]
                    .replaceFirst(CommonClassNameMatcher.L1_SPLIT_STR, " ").equals(answer);
            if (success) writer.write("V ");
            else writer.write("X ");
            writer.write(query + " ---expect--> " + answer + "\n");
            for (String result : results) {
                String[] _tmp = result.split(CommonClassNameMatcher.DELIMITER);
                String _language = _tmp[0].replaceFirst(CommonClassNameMatcher.L1_SPLIT_STR, ":");
                String _componentName = _tmp[1];
                String _className = _tmp[2];
                String score = String.format("%.4f", Float.parseFloat(_tmp[3]));
                writer.write(String.format("%s > %s | %s  %s%n", _language, _componentName, _className, score));
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
