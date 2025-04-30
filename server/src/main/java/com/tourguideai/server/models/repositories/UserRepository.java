package com.tourguideai.server.models.repositories;

import java.util.Optional;

import org.springframework.data.jpa.repository.JpaRepository;
import com.tourguideai.server.models.entities.User;

public interface UserRepository extends JpaRepository<User, Long> {
    Optional<User> findByUsername(String username);
}
