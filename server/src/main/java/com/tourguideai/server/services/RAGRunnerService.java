package com.tourguideai.server.services;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

import com.tourguideai.server.models.QueryRequest;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.InputStream;
import java.util.concurrent.CompletableFuture;
@Service
public class RAGRunnerService {
    @Value("${tourguide.script.path}")
    private String scriptPath;
    @Value("${tourguide.python.interpreter}")
    private String pythonInterpreter;

    public CompletableFuture<String> runRagQuery(QueryRequest query) {
        return CompletableFuture.supplyAsync(() -> {
            try {
                ProcessBuilder processBuilder = new ProcessBuilder(
                    pythonInterpreter,
                    scriptPath,
                    query.getQuery());
                processBuilder.redirectErrorStream(true);
                Process process = processBuilder.start();

                // Capture the output from the Python script
                InputStream inputStream = process.getInputStream();
                BufferedReader reader = new BufferedReader(new InputStreamReader(inputStream));
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
        });
    }
    public void runRagQueryStream(String query, SseEmitter emitter) {
        CompletableFuture.runAsync(() -> {
            try {
                ProcessBuilder processBuilder = new ProcessBuilder(
                    pythonInterpreter,
                    scriptPath,
                    query
                );
                processBuilder.redirectErrorStream(true);
                Process process = processBuilder.start();
    
                InputStream in = process.getInputStream();
                byte[] buf = new byte[64];
                int len;
                while ((len = in.read(buf)) != -1) {
                    String chunk = new String(buf, 0, len);
                    for (String word : chunk.split("\\s+")) {
                        emitter.send(SseEmitter.event().data(word + " "));
                    }
                }
                process.waitFor();
                emitter.complete();
            } catch (Exception e) {
                emitter.completeWithError(e);
                e.printStackTrace();
            }
        });
    }    
}
