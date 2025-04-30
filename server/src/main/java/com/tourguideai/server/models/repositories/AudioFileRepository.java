package com.tourguideai.server.models.repositories;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import com.tourguideai.server.models.entities.AudioFile;

/**
 * Repository interface for AudioFile entities.
 */
@Repository
public interface AudioFileRepository extends JpaRepository<AudioFile, Long> {
    // Additional query methods (if needed) can be defined here
}