# Albert Heijn Recommendation with LLM

A recommendation system that leverages LLMs to identify Albert Heijn products on discount and formulate healthy recipe recommendations. It automates sending these recommendations via email on odd weekdays (Monday, Wednesday, Friday) to align with shopping routines, operating within GitHub Codespaces and automated via GitHub Actions.

![Workflow](data/img/knowledge-graph_sample.png)

## Features

* **Data Ingestion:**
    * Processes Albert Heijn bonus items from structured JSON data.
    * Supports flexible data input methods for bonus item acquisition. [Framework Overview](data/docs/Medium.md)
* **LLM-Powered Recommendation:**
    * Uses **GitHub-hosted LLMs** (e.g., models available through the [GitHub platform](https://github.com/explore/topics/machine-learning) or integrated via GitHub Codespaces) for natural language understanding and generation.
    * Identifies optimal discount opportunities.
    * Generates diverse and healthy recipe recommendations based on available discounted products.

    ![Prompt](data/img/knowledge-graph-prompt.png)
        ![Suggestions](data/img/knowledge-graph-prompt.png)
    ![Items](data/img/knowledge-graph-prompt.png)

* **Embedding and Vector Database:**
    * Leverages **GitHub-compatible embedding models** (e.g., available via [GitHub's machine learning resources](https://github.com/explore/topics/machine-learning)) for generating vector embeddings.
    * Enables efficient similarity searches and retrieval-augmented generation (RAG) to connect products with recipe ingredients and nutritional data.

* **Email Generation & Automation:**
    * Generates well-structured HTML emails, displaying recommended products and recipes in an engaging format.
    * Automated daily execution via GitHub Actions, specifically scheduled for odd weekdays (Mon, Wed, Fri) to deliver timely recommendations before shopping.
* **Visualization:** (Potentially for internal insights or future external features)
![Items](data/html/generated_email.html)

## Project Structure:

Designed with scalability and modularity in mind, allowing for easy extension and customization for data sourcing and recommendation logic. Detail graph is accessed here @ [AH_Recommendation_with_LLM_Public](https://Karthick-840.github.io/AH_Recommendation_with_LLM_Public)

![Project Structure](data/img/project_strucutre.png)

## Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd AH_Recommendation_with_LLM
    ```
2.  **Create & Activate the virtual environment (recommended):**
    ```bash
    chmod +x project_setup.sh
    ./project_setup.sh
    ```
3.  **Configure environment variables:**
    * Create a `config.yml` file in the root directory.
    * Update the credentials, SendPulse API keys, and any specific data paths as per the need.

## Usage

1.  Run the main script (typically within GitHub Codespaces or via GitHub Actions)
    ```bash
    python main.py
    ```
2.  Update Temperature setting for LangGraph as per need in `extract_image_information.py`, compatible with the **GitHub-hosted LLMs**.

    ![HTML Output](data/img/reponse.png)
3.  **Automated Email Delivery:** The system is set up to run periodically via GitHub Actions, sending emails on odd weekdays. For testing and deployment, ensure GitHub Secrets are configured for SendPulse API.

    ![Functionality](data/img/conversation.png)

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues to suggest improvements or report bugs.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact
[Karthick Jayaraman](https://www.linkedin.com/in/karthick840) 
