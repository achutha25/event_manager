## Issues in the event_manager Project

## No.1
Issue discussed in the instructor video:
[Issue 1](https://github.com/achutha25/event_manager/tree/1-openapi-docs-page-login-and-register-example-data-mismatch#)

In my user_schemas.py file, I identified that the UserResponse model had a duplicate definition for the field "role," which caused a conflict during model instantiation. I removed the extra definition, ensuring that "role" is declared only once in the model. I also discovered that importing built-in types from the builtins module was unnecessary, so I removed those imports to clean up the code. Additionally, I updated the UUID example in the UserResponse model to use a string representation of a valid UUID, improving consistency and clarity. I corrected the sample dictionary in the UserListResponse model by eliminating duplicated keys such as "bio" and "role," which previously led to confusion. These modifications collectively resolved the validation errors and improved the maintainability and reliability of my schema definitions.