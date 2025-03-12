# Google Scholar Alert Processor
Automated processing of Google Scholar email alerts using AI classification to identify relevant research articles.

*Disclaimer: This tool uses AI-generated code, including this README.md, from DeepSeek models. Always review and test code thoroughly before deployment. Use at your own risk.*

## Features

- 📧 Automatic scanning of Gmail for unread Scholar alerts
- 🧠 LLM-powered relevance classification (Yes/No/n.a.)
- 📊 Excel export with timestamped partial/final results
- 🔐 Secure OAuth2 authentication via Google API
- 🔄 Compatible with any OpenAI-style API endpoints

## Setup Instructions

### Prerequisites
- Python 3.11+ (recommend using **[uv](https://docs.astral.sh/uv/)**)
- Google Cloud Project with **Gmail API enabled**
- LLM API key (Fireworks.ai, OpenAI, etc.)

### Configuration

1. **Google Credentials**  
   - Follow Google's [Python Quickstart Guide](https://developers.google.com/gmail/api/quickstart/python)
   - Save downloaded credentials as `credentials.json`  
     *⚠️ Never share this file or the `token.json` file!*

2. **Research Criteria**  
   Edit `llm_classify_article.py`:
   ```python
   # Set your research focus here
   USER_CRITERIA = """[Describe your research focus in detail]"""
   ```

3. **LLM Configuration**  
   Create `.env` file (copy from `.envsample`):
   ```bash
   # Example for Fireworks.ai
   LLM_API_URL='https://api.fireworks.ai/inference/v1'
   LLM_API_KEY='your-api-key-here'
   ```

4. **Install Dependencies**
   ```bash
   uv pip install -r requirements.txt
   ```

## Usage

```bash
# Run with environment variables
uv run --env-file .env read-email.py
```

On the first run, read the lines carefully, a login link will be shared. Open the link in a safe browser and login using your Gmail account. Maybe, the program will try to open the link using the console browser. It did not work. Just quit the console browser and open the link in a graphical browser.

Output files will be saved as:
- `partial_YYYYMMDD_HHMMSS.xlsx` (periodic backups)
- `final_YYYYMMDD_HHMMSS.xlsx` (completed processing)

## Customization

### Modify Email Query
In `read-email.py`:
```python
# Example: Only process alerts with attachments
q = "is:unread from:scholaralerts-noreply@google.com has:attachment"
```

### Change LLM Model
In `llm_interface.py`:
```python
# Example for Llama model model
MODEL = "accounts/fireworks/models/llama-v3p1-405b-instruct"
```

## Security Notice

⚠️ **Critical Security Practices**
- Audit code before execution
- Never commit sensitive files (`*.json`, `*.env`) to version control

---

*Disclaimer: This tool uses AI-generated code from DeepSeek models. Always review and test code thoroughly before deployment. Use at your own risk.*

