package xjf;

import java.io.IOException;
import java.io.FileWriter;

import org.apache.lucene.queryparser.classic.ParseException;

import org.junit.BeforeClass;
import org.junit.Test;


import static org.junit.Assert.assertTrue;

public class PackageMatcherTest {
    private static CommonPackageMatcher commonMatcher, javaMatcher, javascriptMatcher, pythonMatcher;
    //
    @BeforeClass
    public static void beforeClass() throws IOException {
        long startTime = System.currentTimeMillis();
        commonMatcher = new CommonPackageMatcher(new String[] {
//                "../../components_data/eco_name_dataset_for_lucene/go_components",
//                "../../components_data/eco_name_dataset_for_lucene/mvn_components_total",
//                "../../components_data/eco_name_dataset_for_lucene/npm_components_processed",
                "../../components_data/eco_name_dataset_for_lucene/filtered_pypi_components"

        });
        pythonMatcher = new PythonPackageMatcher(new String[] {
                "../../components_data/eco_name_dataset_for_lucene/filtered_pypi_components"

        });
        long endTime = System.currentTimeMillis();
        System.out.println("Time cost: " + (endTime - startTime) / 1000.0 + "s.");
    }

    @Test
    public void pythonMatcherTest() throws IOException, ParseException {
        oneToOneTest(pythonMatcher, "borgbackup", "borg", "borgbackup");
    }

    private boolean oneToOneTest(CommonPackageMatcher matcher, String vendor, String product, String answer) throws IOException, ParseException {
        String[] results = matcher.search(vendor, product);
        String query = vendor + ":" + product;

        String filename = String.format("pythonPackageMatcherTest_%s_%s.txt", product, vendor);

        try {
            FileWriter writer = new FileWriter(filename);

            if (results.length < 1) {
                writer.write("X " + query + " ---expect--> " + answer + "\n");
                writer.write("   > ------  --------\n");
                return false;
            }
            boolean success = results[0].split(CommonPackageMatcher.DELIMITER)[0]
                    .replaceFirst(CommonPackageMatcher.L1_SPLIT_STR, ":").equals(answer);
            if (success) writer.write("V ");
            else writer.write("X ");
            writer.write(query + " ---expect--> " + answer + "\n");
            for (String result : results) {
                String[] _tmp = result.split(CommonPackageMatcher.DELIMITER);
                String language = _tmp[0];
                String pkg = _tmp[1].replaceFirst(CommonPackageMatcher.L1_SPLIT_STR, ":");
                String score = String.format("%.4f", Float.parseFloat(_tmp[2]));
                writer.write(String.format("   > %s %s  %s%n", language, score, pkg));
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
