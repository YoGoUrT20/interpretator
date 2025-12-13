# AI Model Interpreter & Ranker

A Python tool that leverages multiple AI model requests to generate diverse answers to a single prompt, and then uses a judge model to evaluate and rank the best responses.

## Features

*   **Concurrent Generation**: Sends multiple requests in parallel to an AI model (e.g., GPT-3.5) to gather diverse perspectives or attempts.
*   **AI Ranking**: Uses a more powerful model (e.g., GPT-4) to analyze all generated responses and select the best ones.
*   **Markdown Outputs**: Saves every individual response and the final ranking analysis as Markdown files for easy reading.
*   **Rich CLI**: Beautiful command-line interface with progress bars and status updates.
*   **Configurable**: Easy-to-adjust settings for models, request counts, and ranking criteria.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/YoGoUrT20/interpretator.git
    cd interpretator
    ```

2.  **Install dependencies:**
    It is recommended to use a virtual environment.
    ```bash
    pip install -r requirements.txt
    ```

3.  **Environment Setup:**
    Create a `.env` file in the root directory and add your OpenRouter API key:
    ```env
    OPENROUTER_API_KEY=your_api_key_here
    ```

## Configuration

You can customize the behavior by editing `settings.py`:

```python
# Model Settings
INITIAL_INTERPRETER_MODEL = "openai/gpt-3.5-turbo" # Model for generating answers
BEST_ANSWERS_SELECTOR_MODEL = "openai/gpt-4o"      # Model for ranking answers

# Execution Settings
INTERPRETATION_REQUESTS_AMOUNT = 10  # Number of answers to generate
BEST_ANSWERS_AMOUNT = 1              # Number of top answers to select
```

## Usage

Run the main script:

```bash
python main.py
```

1.  Enter your question or prompt when asked.
2.  The tool will generate `INTERPRETATION_REQUESTS_AMOUNT` responses in parallel.
3.  It will then send all responses to the judge model for evaluation.
4.  Results are displayed in the terminal and saved to the `outputs/` directory.

## Output Structure

*   `outputs/response_X.md`: Individual responses from the generation phase.
*   `outputs/final_ranking.md`: The final evaluation and ranking by the judge model.
