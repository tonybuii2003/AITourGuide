package com.tourguideai.server.services;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Map;
import java.util.UUID;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.ResponseEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import com.tourguideai.server.models.entities.User;
import com.tourguideai.server.models.entities.AudioFile;
import com.tourguideai.server.models.repositories.UserRepository;
import com.tourguideai.server.models.repositories.AudioFileRepository;

import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.beans.factory.annotation.Value;



@Service
public class VoiceAssistantService {
    private final String pythonInterpreter;
    private final String voiceScript;
    private static final Logger log =
        LoggerFactory.getLogger(VoiceAssistantService.class);
    private static final Path UPLOAD_DIR = Paths.get("ai/uploads");

    private final UserRepository      userRepo;
    private final AudioFileRepository audioFileRepo;
    private final BCryptPasswordEncoder passwordEncoder;


    public VoiceAssistantService(UserRepository userRepo,
                                AudioFileRepository audioFileRepo, BCryptPasswordEncoder passwordEncoder,
                                @Value("${tourguide.python.interpreter}") String pythonInterpreter,
                                @Value("${tourguide.voice.script.path}") String voiceScript) {
                                    
        this.passwordEncoder = passwordEncoder;
        this.userRepo      = userRepo;
        this.audioFileRepo = audioFileRepo;
        this.pythonInterpreter = pythonInterpreter;
        this.voiceScript      = voiceScript;
        try {
            Files.createDirectories(UPLOAD_DIR);
        } catch (IOException e) {
            throw new RuntimeException("Could not create upload dir", e);
        }
    }

    public ResponseEntity<byte[]> processGuestAudio(String guestId,
                                                    MultipartFile audioFile)
            throws IOException, InterruptedException {
        // validation
        if (audioFile.isEmpty()) {
            return ResponseEntity
                .badRequest()
                .body(null);
        }

        // find or create guest
        User guest = userRepo
            .findByUsername(guestId)
            .orElseGet(() -> {
                String dummy = passwordEncoder.encode("guest");
                User u = new User();
                u.setUsername(guestId);
                u.setPasswordHash(dummy);
                return userRepo.save(u);
            });

        log.info("Streaming assistant for guest {}", guestId);

        // write upload to disk
        String inFilename = UUID.randomUUID() + "_"
                          + Path.of(audioFile.getOriginalFilename())
                                .getFileName()
                                .toString();
        Path inPath = UPLOAD_DIR.resolve(inFilename);
        Files.write(inPath, audioFile.getBytes());

        // persist metadata
        AudioFile record = new AudioFile();
        record.setOwner(guest);
        record.setFileName(inFilename);
        record.setContentType(audioFile.getContentType());
        record.setSize(audioFile.getSize());
        audioFileRepo.save(record);

        // launch Python, streaming in, streaming out
        ProcessBuilder pb = new ProcessBuilder(
            pythonInterpreter,
            voiceScript,
            "--stdin",
            "--stdout"
        );
        pb.redirectError(ProcessBuilder.Redirect.INHERIT);
        Process proc = pb.start();

        // stream upload -> python stdin
        try (InputStream in = audioFile.getInputStream();
             OutputStream pyIn = proc.getOutputStream()) {
            in.transferTo(pyIn);
        }
        proc.getOutputStream().close();

        // capture stdout into a buffer
        ByteArrayOutputStream buf = new ByteArrayOutputStream();
        try (InputStream pyOut = proc.getInputStream()) {
            pyOut.transferTo(buf);
        }

        int exit = proc.waitFor();
        if (exit != 0) {
            log.error("Assistant process exited with {}", exit);
            return ResponseEntity
                .status(500)
                .body(null);
        }

        byte[] reply = buf.toByteArray();
        return ResponseEntity.ok()
            .header(HttpHeaders.CONTENT_DISPOSITION, "inline; filename=\"reply.wav\"")
            .contentType(MediaType.parseMediaType("audio/wav"))
            .body(reply);
    }
}