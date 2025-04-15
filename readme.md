## Issues in the event_manager Project


## No.1--Issue discussed in the instructor video--openapi-docs-page-login-and-register-example-data-mismatch
[Issue 1](https://github.com/achutha25/event_manager/tree/1-openapi-docs-page-login-and-register-example-data-mismatch#)

In my user_schemas.py file, I identified that the UserResponse model had a duplicate definition for the field "role," which caused a conflict during model instantiation. I removed the extra definition, ensuring that "role" is declared only once in the model. I also discovered that importing built-in types from the builtins module was unnecessary, so I removed those imports to clean up the code. Additionally, I updated the UUID example in the UserResponse model to use a string representation of a valid UUID, improving consistency and clarity. I corrected the sample dictionary in the UserListResponse model by eliminating duplicated keys such as "bio" and "role," which previously led to confusion. These modifications collectively resolved the validation errors and improved the maintainability and reliability of my schema definitions.


## No.2--:remove-duplicate-login-endpoint
[Issue 2](https://github.com/achutha25/event_manager/tree/2-remove-duplicate-login-endpoint)

The FastAPI application contained two login endpoints both mapped to the "/login/" path, which created ambiguous routing and potential conflicts during authentication requests. This duplication led to uncertainty regarding which endpoint would handle incoming login requests, causing inconsistent behavior. After careful review, I discovered that one endpoint was intended for inclusion in the API schema while the duplicate was marked with include_in_schema=False. I resolved the issue by removing the duplicate login endpoint, thereby leaving only a single, consistent endpoint to manage user authentication. I then verified that the remaining endpoint correctly validates credentials and returns a valid access token, ensuring that the authentication flow remains intact. This change not only streamlined the API routing but also improved code clarity and maintainability.

## No.3--Clean Up EmailService and Resolve SMTP Connection Issues
[Issue 3](https://github.com/achutha25/event_manager/tree/3-clean-up-emailservice-and-resolve-smtp-connection-issues)

The EmailService implementation previously imported unnecessary built-in types, which added clutter to the code. I noticed that the SMTP connection was triggering disconnections during the login phase, causing email sending failures. To address this, I ensured that the settings configuration was correctly passed to the SMTPClient constructor. I removed redundant imports such as ValueError, dict, and str since these are available by default in Python. I confirmed that the send_user_email method correctly maps email types to subject lines and renders HTML content via the TemplateManager. I also added inline comments to improve code clarity and maintainability. These changes have resolved the SMTP connection issues and streamlined the email service functionality for sending verification emails.

## No.4--Fix Invalid UUID Format in Non-Existent User Tests
[Issue 4](https://github.com/achutha25/event_manager/tree/4-fix-invalid-uuid-format-in-non-existent-user-tests)

The user service tests were failing because an invalid string ("non-existent-id") was used where a valid UUID was required. This invalid input caused UUID conversion errors and led to unexpected exceptions during test execution. I identified the root cause by reviewing the error logs and pinpointed the tests for fetching and deleting non-existent users. To resolve this, I replaced the invalid string with a properly formatted UUID, "123e4567-e89b-12d3-a456-426614174000". This valid UUID is guaranteed not to exist in the database, ensuring that the service functions return None or False as expected. After implementing the change, the tests for non-existent users now pass successfully without causing conversion errors. These modifications improved type consistency across the tests and enhanced the overall reliability of the user service.


