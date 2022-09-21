package com.teammspaint.stemdatadashboard.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import com.teammspaint.stemdatadashboard.dao.User;

@Repository
public interface UserRepository extends JpaRepository<User, Long> {

    /**
     * Returns the User object corresponding to the specified email address.
     * 
     * @param email The user's email address.
     * @return The User object representing the user. If it doesn't exist, 
     * null is returned.
     */
    @Query("SELECT 1 FROM USERS U WHERE U.EMAIL_ADDRESS = :email")
    public User findByEmail(@Param("email") String email);

    /**
     * Returns whether or not the user is an admin.
     * 
     * @param email The user's email address.
     * @return A boolean representing if the user is an admin or not.
     */
    @Query("SELECT IS_ADMIN FROM USERS U WHERE U.EMAIL_ADDRESS = :email")
    public boolean isAdmin(@Param("email") String email);
}
