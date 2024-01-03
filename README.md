# Facebook posts scraping project

This project provides a Python-based web scraping solution for extracting information from Facebook posts. It includes functionalities for scraping posts on facebook.com, by creating search URLs based on search keys, extracting hyperlinks from the post content which matches a specified pattern using regular expressions, and retrieving all the comments on each post.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)
- [GitHub Actions Workflow](#GithubActionsWorkflow)

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/huo1m1w1/facebook_scraping_project.git
   cd your_project

2. Install dependencies:


    ```bash
    poetry install

3. Set up configuration:

    Create a secret.yaml file with necessary credentials to log in to facebook.
    ```yaml
    credentials:
        username: xxxxxxxxxxxx
        password: xxxxxx


## Usage
    Describe how to use your project. Provide examples if applicable.
    ```bash
    poetry run python src/fb_scraping_project/main.py


## Testing
    To run tests, use the following command:
    ```bash
    poetry run pytest


## Contributing
If you'd like to contribute, please follow these guidelines:

Fork the repository.
Create a new branch.
Make your changes.
Submit a pull request.
## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE.txt) file for details.

## GitHub Actions Workflow

This project includes a GitHub Actions workflow for continuous integration. The workflow is automatically triggered on every push to the repository.

2. Workflow Status

[![Python CI](https://github.com/huo1m1w1/facebook_scraping_project/actions/workflows/main.yml/badge.svg)](https://github.com/huo1m1w1/facebook_scraping_project/actions/workflows/main.yml)


3. Workflow Details

The workflow performs the following tasks:

- Runs tests using Pytest to ensure code reliability.
- Other steps or tasks specific to your project.

For more details, check the [.github/workflows/main.yml](.github/workflows/main.yml) file.
