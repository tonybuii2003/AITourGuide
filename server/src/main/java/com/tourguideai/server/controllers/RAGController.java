package com.tourguideai.server.controllers;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import com.tourguideai.server.services.RAGRunnerService;

import com.tourguideai.server.models.QueryResponse;
import com.tourguideai.server.models.QueryRequest;


@RestController
@RequestMapping("/api")
public class RAGController {
    private final RAGRunnerService ragService;

    @Autowired
    public RAGController(RAGRunnerService ragRunnerService) {
        this.ragService = ragRunnerService;
    }

    @PostMapping("/rag")
    public ResponseEntity<QueryResponse> askRag(@RequestBody QueryRequest request) {
        String answer = ragService.runRagQuery(request);
        return ResponseEntity.ok(new QueryResponse(answer));
    }
}
