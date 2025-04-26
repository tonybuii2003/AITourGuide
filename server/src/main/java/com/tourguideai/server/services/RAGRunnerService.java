package com.tourguideai.server.services;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

import com.tourguideai.server.models.QueryRequest;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.io.InputStream;
import java.util.concurrent.CompletableFuture;
@Service
public class RAGRunnerService {
    @Value("${tourguide.script.path}")
    private String scriptPath;
    @Value("${tourguide.python.interpreter}")
    private String pythonInterpreter;
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
                byte[] buf = new byte[1024];
                int len;
                while ((len = in.read(buf)) != -1) {
                    // decode exactly what Python printed, spaces & all
                    String chunk = new String(buf, 0, len, StandardCharsets.UTF_8);
                    // send it as one SSE event
                    emitter.send(SseEmitter.event().data(chunk));
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
