// src/main/java/com/tourguideai/server/controllers/VoiceAgentController.java
package com.tourguideai.server.controllers;

import java.io.IOException;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;

import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import org.springframework.web.multipart.MultipartFile;

import com.tourguideai.server.services.VoiceAssistantService;

@RestController
@RequestMapping("/api")
@CrossOrigin(origins = "https://curatai.tonybui.dev/")
public class VoiceAgentController {
    private final VoiceAssistantService assistantService;

    @Autowired
    public VoiceAgentController(VoiceAssistantService assistantService) {
        this.assistantService = assistantService;
    }

    @PostMapping(value = "/guests/{guestId}/audio", consumes = "multipart/form-data")
    public ResponseEntity<byte[]> handleGuestAudio(
        @PathVariable String guestId,
        @RequestParam("audio") MultipartFile audioFile
    ) throws IOException, InterruptedException {
        return assistantService.processGuestAudio(guestId, audioFile);
    }
}
