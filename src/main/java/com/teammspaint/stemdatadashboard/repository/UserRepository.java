package com.teammspaint.stemdatadashboard.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.CrudRepository;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import com.teammspaint.stemdatadashboard.dao.User;

@Repository
public interface UserRepository extends JpaRepository<User, Long> {

    // @Query("SELECT * FROM USERS U WHERE U.EMAIL_ADDRESS = :email")
    // public User getUserByEmail(@Param("email") String email);
}
