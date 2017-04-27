/** Import il1 classes. */
import edu.ucla.belief.*;
import edu.ucla.belief.inference.*;
import edu.ucla.belief.io.PropertySuperintendent;
import edu.ucla.belief.io.NetworkIO;

/** Import classes for loopy belief propagation. */
import edu.ucla.belief.approx.PropagationEngineGenerator;
import edu.ucla.belief.approx.BeliefPropagationSettings;
import edu.ucla.belief.approx.PropagationInferenceEngineImpl;

import java.io.FileReader;
import java.math.BigInteger;

/** Import standard Java classes. */
import java.util.*;

import org.json.simple.JSONArray;
import org.json.simple.JSONObject;
import org.json.simple.parser.JSONParser;


// This class demonstrates code for a probability query

// To compile this class, make sure
// inflib.jar occurs in the command line classpath,
// e.g. javac -classpath inflib.jar MVPQuery.java

// To run it, do the same,
// but also include the path to
// the compiled class,
// e.g. java -classpath .:inflib.jar MVPQuery

// @author Keith Cascio
// @since Apr 26, 2017 4:50:17 PM

public class MVPQuery {
	/** Test. */
	public static void main(String[] args){
		MVPQuery T = new MVPQuery();
		T.doProbabilityQuery(T.readNetworkFile());
	}

	// Demonstrates a probability query.
	public void doProbabilityQuery( BeliefNetwork bn )
	{
		/* Define evidence, by id. */
//      Map evidence = Collections.EMPTY_MAP;
        String path = "/Users/dongjoonkim/NBA_MVP_Capstone/NBA_MVP_Predictor/2017.json";
        JSONArray jsonArray;
        JSONParser parser = new JSONParser();
        try {
            jsonArray = (JSONArray) parser.parse(new FileReader(path));
        } catch (Exception e) {
            System.err.println( "Error, failed to read \"" + path + "\": " + e );
            return;
        }

        String predictedMVPWinner = "";
        double winnerProbability = 0;

        for (Object o1 : jsonArray) {
            JSONObject stats = (JSONObject) o1;
            String playerName = (String) stats.get("NAME");

            Set keySet = stats.keySet();
            keySet.remove("W_PCT_RANK");
            keySet.remove("L_RANK");
            keySet.remove("NAME");

            Map<Variable, String> evidence = new HashMap<>();

            for (Object o2 : keySet) {
                String key = (String) o2;
                String value = (String) stats.get(key);
                evidence.put(bn.forID(key), value);
            }

            /* Create the Dynamator(edu.ucla.belief.inference.SynchronizedInferenceEngine). */
            edu.ucla.belief.approx.PropagationEngineGenerator dynamator = new edu.ucla.belief.approx.PropagationEngineGenerator();

		    /* Edit settings. */
            edu.ucla.belief.approx.BeliefPropagationSettings settings = dynamator.getSettings((PropertySuperintendent) bn);
            settings.setTimeoutMillis(10000);
            settings.setMaxIterations(100);
            settings.setScheduler(edu.ucla.belief.approx.MessagePassingScheduler.TOPDOWNBOTTUMUP);
            settings.setConvergenceThreshold(1.0E-7);

		    /* Create the InferenceEngine. */
            InferenceEngine engine = dynamator.manufactureInferenceEngine(bn);

		    /* Set evidence. */
            try {
                bn.getEvidenceController().setObservations(evidence);
            } catch( StateNotFoundException e ){
                System.err.println( "Error, failed to set evidence: " + e );
                return;
            };

		    /* Calculate Marginal with all evidence. */
            double marginalProbability  = engine.probability();
            System.out.println("Marginal of evidence is " + marginalProbability);

            evidence.put(bn.forID("MVP"), "True");

            /* Set evidence with MVP to calculate joint probability. */
            try {
                bn.getEvidenceController().setObservations(evidence);
            } catch( StateNotFoundException e ){
                System.err.println( "Error, failed to set evidence: " + e );
                return;
            };

            double jointProbability = engine.probability();
            System.out.println("Marginal of evidence is " + jointProbability);

            double probabilityMVPGivenEvidence = jointProbability / marginalProbability;
            System.out.println("Probability that " + playerName + " will win MVP is " + probabilityMVPGivenEvidence);

            if (winnerProbability < probabilityMVPGivenEvidence) {
                predictedMVPWinner = playerName;
                winnerProbability = probabilityMVPGivenEvidence;
            }

            /*
            Warning: you chose to calculate marginals for only those
            variables for which monitors were visible, but there were
            no such variables.
            */

		    /* Clean up to avoid memory leaks. */
            engine.die();
        }

        System.out.println("Predicted winner is " + predictedMVPWinner + " with " + winnerProbability + " chance.");
	}


	// Open the network file used to create this tutorial.
	public BeliefNetwork readNetworkFile()
	{
		String path = "/Users/dongjoonkim/NBA_MVP_Capstone/NBA_MVP_Predictor/three_pos_rank.net";

		BeliefNetwork ret = null;
		try {
			/* Use NetworkIO static method to read network file. */
			ret = NetworkIO.read( path );
		} catch(Exception e) {
			System.err.println( "Error, failed to read \"" + path + "\": " + e );
			return null;
		}

        return ret;
	}
}
