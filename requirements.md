# Coding Assignment: File Server and CLI Implementation

## Objective:

The goal of this assignment is to assess your ability to design and implement a file server that can be run in a Docker
container. Additionally, you will create a command-line interface (CLI) to interact with the file server. This
assignment will test your skills in server development, containerization, and CLI tool creation.

## Task Description:

1. File Server Implementation:
    - Develop a file server that supports the following operations:
    - Upload File: Allow users to upload files to the server.
    - Download File: Enable users to download files from the server.
    - List Files: Provide a list of all files stored on the server.
    - Delete File: Allow users to delete files from the server.
    - The server should be able to handle multiple concurrent requests efficiently.
    - Ensure proper error handling and validation for each operation.
2. Docker Containerization:
    - Containerize the file server using Docker.
    - Provide a Dockerfile that specifies the environment and dependencies required to run the server.
    - Ensure that the server can be easily started and stopped using Docker commands.
3. Command-Line Interface (CLI):
    - Implement a CLI tool that interacts with the file server.
    - The CLI should support the following commands:
    - `upload <file_path>`: Upload a file to the server.
    - `download <file_name>`: Download a file from the server.
    - `list`: List all files stored on the server. 
    - `delete <file_name>`: Delete a file from the server.
    - Ensure that the CLI provides clear and informative feedback to the user for each operation.

## Submission Requirements:

- Provide the source code for the file server and CLI tool.
- Include a README file with instructions on how to build and run the Docker container, as well as how to use the CLI
  tool.
- Ensure your code is well-documented and follows best practices for readability and maintainability.

## Evaluation Criteria:

- Functionality: The file server and CLI tool should work as specified and handle edge cases gracefully.
- Code Quality: Code should be clean, well-organized, and follow best practices.
- Documentation: Clear instructions and documentation should be provided.
- Efficiency: The server should handle multiple concurrent requests efficiently.
- Creativity: Any additional features or improvements will be considered a plus.
