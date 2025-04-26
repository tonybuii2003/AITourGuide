package com.tourguideai.server.controllers;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;
import org.springframework.http.MediaType;

import com.tourguideai.server.models.QueryRequest;
import com.tourguideai.server.services.RAGRunnerService;

@RestController
@RequestMapping("/api")
@CrossOrigin(origins = {"https://nwreoxk-anonymous-8081.exp.direct/", "https://curatai.tonybui.dev/", "http://localhost:8082/"})
public class RAGController {
    private final RAGRunnerService ragService;

    @Autowired
    public RAGController(RAGRunnerService ragRunnerService) {
        this.ragService = ragRunnerService;
    }

    @PostMapping(
    value    = "/rag/stream",
    consumes = MediaType.APPLICATION_JSON_VALUE,
    produces = MediaType.TEXT_EVENT_STREAM_VALUE
    )
    public SseEmitter streamRag(@RequestBody QueryRequest request) {
        SseEmitter emitter = new SseEmitter();
        ragService.runRagQueryStream(request.getQuery(), emitter);
        return emitter;
    }
}
