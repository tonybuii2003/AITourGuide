package com.tourguideai.server.services;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import com.tourguideai.server.models.QueryRequest;

import java.io.BufferedReader;
import java.io.InputStreamReader;
@Service
public class RAGRunnerService {
    @Value("${tourguide.script.path}")
    private String scriptPath;
    @Value("${tourguide.python.interpreter}")
    private String pythonInterpreter;

    public String runRagQuery(QueryRequest query) {
        try {
            ProcessBuilder processBuilder = new ProcessBuilder(
                pythonInterpreter,
                scriptPath,
                query.getQuery());
            processBuilder.redirectErrorStream(true);
            Process process = processBuilder.start();

            // Capture the output from the Python script
            BufferedReader reader = new BufferedReader(new InputStreamReader(process.getInputStream()));
            StringBuilder output = new StringBuilder();
            String line;
            while ((line = reader.readLine()) != null) {
                output.append(line).append("\n");
            }
            int exitCode = process.waitFor();
            String fullOutput = output.toString().trim();
            if (exitCode != 0) {
                return "Error: Python script exited with code " + exitCode + ". Details: " + fullOutput;
            }
            return output.toString().trim();
        } catch (Exception e) {
            e.printStackTrace();
            return "Exception occurred: " + e.getMessage();
        }
    }
}
