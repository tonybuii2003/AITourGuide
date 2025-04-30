package com.tourguideai.server.models.entities;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Table;
import jakarta.persistence.Id;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.PrePersist;
import jakarta.persistence.JoinColumn;
import java.time.Instant;

@Entity
@Table(name = "audio_files")
public class AudioFile {
  @Id @GeneratedValue private Long id;

  @ManyToOne
  @JoinColumn(name = "user_id", nullable = false)
  private User owner;

  private String filename;
  private String contentType;
  private long   size;
  @Column(name = "uploaded_at", nullable = false, updatable = false)
  private Instant uploadedAt;

  // getters/setters
    @PrePersist
    protected void onCreate() {
        this.uploadedAt = Instant.now();
    }
    public Long getId() {
        return id;
    }
    public void setId(Long id) {
        this.id = id;
    }

    public User getOwner() {
        return owner;
    }
    public void setOwner(User owner) {
        this.owner = owner;
    }

    public String getFileName() {
        return filename;
    }
    public void setFileName(String filename) {
        this.filename = filename;
    }

    public String getContentType() {
        return contentType;
    }
    public void setContentType(String contentType) {
        this.contentType = contentType;
    }
    public long getSize() {
        return size;
    }
    public void setSize(long size) {
        this.size = size;
    }
    public Instant getUploadedAt() {
        return uploadedAt;
    }
    public void setUploadedAt(Instant uploadedAt) {
        this.uploadedAt = uploadedAt;
    }

}

