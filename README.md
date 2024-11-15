# Authentication and Profile API Documentation

This document provides an overview of the authentication and profile API routes. Use this guide to understand how to connect to each route and build the UI components for authentication and profile management features.

## Overview
The API provides routes for:
- Registering teachers and students
- Logging in and out users
- Accessing and updating user profile information
- Deleting user accounts

**Note**: All requests require a `Content-Type` of `application/json`.

---

## Authentication Routes

### 1. Teacher Registration
**Endpoint**: `/auth/register_teacher`  
**Method**: `POST`  
**Rate Limit**: 5 requests per minute  

Registers a new teacher account.

#### Request Body
- `username` (string, required): Alphanumeric, 3-20 characters.
- `email` (string, required): Valid email format.
- `password` (string, required): Minimum 8 characters.
- `phone_number` (string, required): Numeric, 10-15 digits.
- `first_name` (string, required): Letters and spaces, 2-30 characters.
- `last_name` (string, required): Letters and spaces, 2-30 characters.
- `birth_date` (string, required): Format `YYYY-MM-DD`.
- `gender` (string, required): Options: `MALE` or `FEMALE`.
- `nationality` (string, required): Letters only.
- `country` (string, required): Letters only.
- `time_zone` (string, required): User's time zone.
- `national_id` (string, required): Alphanumeric, 5-20 characters.
- `language` (string, required): Preferred language.

#### Response
- `status` (string): "success"
- `user` (object): Registered user's `username` and `email`
- `message` (string): "Teacher account created and logged in successfully"

### 2. Student Registration
**Endpoint**: `/auth/register_student`  
**Method**: `POST`  
**Rate Limit**: 5 requests per minute  

Registers a new student account.

#### Request Body
- `username` (string, required): Alphanumeric, 3-20 characters.
- `email` (string, required): Valid email format.
- `password` (string, required): Minimum 8 characters.
- `phone_number` (string, required): Numeric, 10-15 digits.
- `first_name` (string, required): Letters and spaces, 2-30 characters.
- `last_name` (string, required): Letters and spaces, 2-30 characters.
- `birth_date` (string, required): Format `YYYY-MM-DD`.
- `gender` (string, required): Options: `MALE` or `FEMALE`.
- `nationality` (string, required): Letters only.
- `country` (string, required): Letters only.
- `time_zone` (string, required): User's time zone.
- `level` (integer, required): Education level or grade.
- `parent_phone_number` (string, required): Parent's phone number, 10-15 digits.
- `language` (string, required): Preferred language.

#### Response
- `status` (string): "success"
- `user` (object): Registered user's `username` and `email`
- `message` (string): "Student account created and logged in successfully"

### 3. Login
**Endpoint**: `/auth/login`  
**Method**: `POST`  
**Rate Limit**: 5 requests per minute  

Logs in a user based on their email and password.

#### Request Body
- `email` (string, required): User's registered email.
- `password` (string, required): User's password.
- `remember_me` (boolean, optional): If true, keeps the user logged in longer.

#### Response
- `status` (string): "success"
- `user` (object): User's `username` and `email`
- `message` (string): "logged in"

### 4. Logout
**Endpoint**: `/auth/logout`  
**Method**: `GET`  

Logs out the currently authenticated user.

#### Response
- `status` (string): "success"
- `message` (string): "User logged out"

---

## Profile Routes

**Blueprint**: `profile`

### 1. Get Profile
**Endpoint**: `/profile/`  
**Method**: `GET`  
**Authentication**: Requires user to be logged in  

Returns the profile details of the currently logged-in user.

#### Response
- User's profile data as a JSON object.

### 2. Update Profile
**Endpoint**: `/profile/update_profile`  
**Method**: `PATCH`  
**Authentication**: Requires user to be logged in  

Updates the profile information of the logged-in user. Only specific fields are allowed for update.

#### Request Body
Allowed fields:
- `first_name` (string): Letters and spaces, 2-30 characters.
- `last_name` (string): Letters and spaces, 2-30 characters.
- `password` (string): At least 8 characters (requires `old_password` to confirm).
- `photo` (string): URL of the user's photo.
- `parent_phone_number` (string): Only for student users.
- `language` (string): Language preference.
- `email` (string): User's email.
- `phone_number` (string): User's phone number.

#### Response
- `status` (string): "success"
- `message` (string): "Profile Updated Successfully" or error message if update fails.

### 3. Delete Account
**Endpoint**: `/profile/delete_account`  
**Method**: `DELETE`  
**Authentication**: Requires user to be logged in  

Deletes the account of the currently logged-in user. The user must provide their password to confirm deletion.

#### Request Body
- `password` (string, required): User's password to confirm deletion.

#### Response
- `status` (string): "success"
- `message` (string): "User Account Deleted Successfully"

---

## Notes
- **Rate limiting** is applied to some routes to prevent abuse. Each route allows a maximum of 5 requests per minute per user.
- **Authorization**: Login, logout, and profile routes are protected and will require a valid session cookie.
