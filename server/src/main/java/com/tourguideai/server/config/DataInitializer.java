package com.tourguideai.server.config;

import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;

import com.tourguideai.server.models.entities.User;
import com.tourguideai.server.models.repositories.UserRepository;

@Component
public class DataInitializer implements CommandLineRunner {

    private final UserRepository userRepo;
    private final BCryptPasswordEncoder passwordEncoder;

    public DataInitializer(UserRepository userRepo) {
        this.userRepo = userRepo;
        this.passwordEncoder = new BCryptPasswordEncoder();
    }

    @Override
    @Transactional
    public void run(String... args) {
        userRepo.findByUsername("guest").orElseGet(() -> {
            User guest = new User();
            guest.setUsername("guest");
            guest.setEmail("guest@example.com");
            String hashed = passwordEncoder.encode("123456");
            guest.setPasswordHash(hashed);
            return userRepo.save(guest);
        });
    }

    @Configuration
    public class SecurityConfig {

        /**
         * Expose BCryptPasswordEncoder so it can be @Autowired elsewhere.
         */
        @Bean
        public BCryptPasswordEncoder passwordEncoder() {
            return new BCryptPasswordEncoder();
        }
    }
}
