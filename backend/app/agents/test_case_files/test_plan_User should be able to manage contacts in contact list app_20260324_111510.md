# Test Plan: Test Plan for User should be able to manage contacts in contact list app

**Test Plan ID:** TP_User_71413a94  
**Jira ID:** User should be able to manage contacts in contact list app  
**Platform:** WEB  
**Framework:** Appium  
**Created:** 2026-03-24T11:15:10.150689  
**Total Test Cases:** 10

## Description
Automated test plan generated from structured requirements: User should be able to manage contacts in contact list app

## Coverage Areas
functional, user-flows

---

## Test Cases

### TC_User_001: User Registration

**Priority:** TestCasePriority.CRITICAL  
**Status:** TestCaseStatus.PENDING  
**Estimated Time:** 15 minutes 
**Tags:** registration, authentication

**Description:** Test case for FR001 - ACAC001

**Preconditions:** User is on registration page

**Expected Outcome:** User is registered successfully

**Test Steps:**

1. **Action:** Enter valid user details  
   **Expected Result:** User is registered successfully
   **Test Data:** Valid user details

---

### TC_User_002: User Login

**Priority:** TestCasePriority.CRITICAL  
**Status:** TestCaseStatus.PENDING  
**Estimated Time:** 15 minutes 
**Tags:** login, authentication

**Description:** Test case for FR001 - ACAC002

**Preconditions:** User is on login page

**Expected Outcome:** User is logged in successfully

**Test Steps:**

1. **Action:** Enter valid user credentials  
   **Expected Result:** User is logged in successfully
   **Test Data:** Valid user credentials

---

### TC_User_003: Invalid User Login

**Priority:** TestCasePriority.CRITICAL  
**Status:** TestCaseStatus.PENDING  
**Estimated Time:** 15 minutes 
**Tags:** login, authentication

**Description:** Test case for FR001 - ACAC003

**Preconditions:** User is on login page

**Expected Outcome:** User is not able to login and an error message is displayed

**Test Steps:**

1. **Action:** Enter invalid user credentials  
   **Expected Result:** Error message is displayed
   **Test Data:** Invalid user credentials

---

### TC_User_004: Add New Contact

**Priority:** TestCasePriority.HIGH  
**Status:** TestCaseStatus.PENDING  
**Estimated Time:** 15 minutes 
**Tags:** contact_management

**Description:** Test case for FR002 - ACAC004

**Preconditions:** User is logged in and on the contacts page

**Expected Outcome:** New contact is added successfully

**Test Steps:**

1. **Action:** Add a new contact with valid details  
   **Expected Result:** New contact is added successfully
   **Test Data:** Valid contact details

---

### TC_User_005: Edit Existing Contact

**Priority:** TestCasePriority.HIGH  
**Status:** TestCaseStatus.PENDING  
**Estimated Time:** 15 minutes 
**Tags:** contact_management

**Description:** Test case for FR002 - ACAC005

**Preconditions:** User is logged in and on the contacts page

**Expected Outcome:** Contact details are updated successfully

**Test Steps:**

1. **Action:** Edit an existing contact with valid details  
   **Expected Result:** Contact details are updated successfully
   **Test Data:** Valid contact details

---

### TC_User_006: Delete Existing Contact

**Priority:** TestCasePriority.HIGH  
**Status:** TestCaseStatus.PENDING  
**Estimated Time:** 15 minutes 
**Tags:** contact_management

**Description:** Test case for FR002 - ACAC006

**Preconditions:** User is logged in and on the contacts page

**Expected Outcome:** Contact is deleted successfully

**Test Steps:**

1. **Action:** Delete an existing contact  
   **Expected Result:** Contact is deleted successfully
   **Test Data:** Existing contact

---

### TC_User_007: View Contacts List

**Priority:** TestCasePriority.HIGH  
**Status:** TestCaseStatus.PENDING  
**Estimated Time:** 15 minutes 
**Tags:** contact_management

**Description:** Test case for FR002 - ACAC007

**Preconditions:** User is logged in and on the contacts page

**Expected Outcome:** All saved contacts are displayed

**Test Steps:**

1. **Action:** View the list of contacts  
   **Expected Result:** All saved contacts are displayed
   **Test Data:** N/A

---

### TC_User_008: Add New Contact with Invalid Details

**Priority:** TestCasePriority.HIGH  
**Status:** TestCaseStatus.PENDING  
**Estimated Time:** 15 minutes 
**Tags:** contact_management

**Description:** Test case for FR002 - ACAC008

**Preconditions:** User is logged in and on the contacts page

**Expected Outcome:** New contact is not added and an error message is displayed

**Test Steps:**

1. **Action:** Add a new contact with invalid details  
   **Expected Result:** Error message is displayed
   **Test Data:** Invalid contact details

---

### TC_User_009: Data Persistence after Refresh/Re-login

**Priority:** TestCasePriority.MEDIUM  
**Status:** TestCaseStatus.PENDING  
**Estimated Time:** 15 minutes 
**Tags:** data_persistence

**Description:** Test case for FR003 - ACAC009

**Preconditions:** User is logged in and has added a new contact

**Expected Outcome:** All saved contacts are still available

**Test Steps:**

1. **Action:** Refresh the page or re-log into the system  
   **Expected Result:** All saved contacts are still available
   **Test Data:** N/A

---

### TC_User_010: Access Control for Contacts Page

**Priority:** TestCasePriority.HIGH  
**Status:** TestCaseStatus.PENDING  
**Estimated Time:** 15 minutes 
**Tags:** access_control

**Description:** Test case for FR004 - ACAC010

**Preconditions:** User is not logged in

**Expected Outcome:** User is redirected to the login page

**Test Steps:**

1. **Action:** Try to access the contacts page  
   **Expected Result:** User is redirected to the login page
   **Test Data:** N/A

---

