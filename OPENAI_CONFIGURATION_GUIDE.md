# Step-by-Step OpenAI Configuration Guide

## Quick Setup (5 minutes)

### Step 1: Get Your OpenAI API Key

1. **Go to OpenAI Platform:**
   - Visit: https://platform.openai.com
   - Sign up or log in with your email

2. **Navigate to API Keys:**
   - Click on your profile (top right)
   - Select "View API keys" or go directly to: https://platform.openai.com/api-keys

3. **Create a New Key:**
   - Click "Create new secret key"
   - Give it a name (e.g., "RAG System Dev")
   - Click "Create secret key"
   - **IMPORTANT:** Copy the key immediately - it starts with `sk-` and you won't see it again!

4. **Save Your Key:**
   - Paste it somewhere safe temporarily (you'll put it in .env next)

### Step 2: Verify Model Access

1. **Check Usage/Billing:**
   - Go to: https://platform.openai.com/usage
   - Ensure you have:
     - Access to GPT-4 (may require approval/credit)
     - Access to embedding models (usually available immediately)

2. **Set Up Billing (if needed):**
   - Go to: https://platform.openai.com/account/billing
   - Add payment method (required for API usage)
   - Set usage limits if desired

### Step 3: Update Your .env File

1. **Open the backend .env file:**
   ```
   backend/.env
   ```

2. **Update these values:**
   ```env
   # Replace with your actual API key
   OPENAI_API_KEY=sk-proj-abc123xyz789...  ← Your key from Step 1
   
   # These are probably fine as-is, but you can change if needed:
   OPENAI_MODEL=gpt-4                    # or gpt-4-turbo, gpt-3.5-turbo
   OPENAI_EMBEDDING_MODEL=text-embedding-ada-002
   ```

3. **Save the file**

### Step 4: Test the Configuration

Run this test to verify it works:

```bash
cd backend
python -c "from app.config import settings; print('✅ OpenAI API Key loaded:', settings.openai_api_key[:10] + '...')"
```

Or create a test script to verify the API works.

## Model Options

### For Chat/Completions:

| Model | Cost | Quality | Speed |
|-------|------|---------|-------|
| `gpt-3.5-turbo` | $0.0015/1K tokens | Good | Fast |
| `gpt-4` | $0.03/1K tokens | Excellent | Medium |
| `gpt-4-turbo` | $0.01/1K tokens | Excellent | Fast |

**Recommendation:** Start with `gpt-4-turbo` (best balance)

### For Embeddings:

| Model | Cost | Dimensions | Quality |
|-------|------|------------|---------|
| `text-embedding-ada-002` | $0.0001/1K tokens | 1536 | Good |
| `text-embedding-3-small` | $0.00002/1K tokens | 1536 | Better |
| `text-embedding-3-large` | $0.00013/1K tokens | 3072 | Best |

**Recommendation:** Use `text-embedding-ada-002` (works with our Azure AI Search setup)

## Common Issues

### "Invalid API key" error
- Check you copied the full key (starts with `sk-`)
- Make sure there are no extra spaces
- Verify the key hasn't expired (regenerate if needed)

### "Model not found" error
- Ensure you have access to GPT-4 (may need approval)
- Try `gpt-3.5-turbo` as a fallback
- Check your billing is set up

### "Insufficient quota" error
- Add payment method at platform.openai.com/account/billing
- Check your usage limits
- Verify you have credits/balance

## Security Reminders

✅ **DO:**
- Keep your API key in `.env` file only
- Never commit `.env` to git
- Rotate keys periodically

❌ **DON'T:**
- Share your API key
- Put it in code files
- Commit it to version control

## Next Steps After Configuration

1. ✅ Test the configuration (see Step 4)
2. ✅ Update Azure AI Search credentials in `.env`
3. ✅ Test document upload and embedding generation
4. ✅ Test chat functionality

## Cost Monitoring

Monitor your usage at:
- https://platform.openai.com/usage
- Set up usage alerts
- Review monthly spending

## Need Help?

- OpenAI Docs: https://platform.openai.com/docs
- API Status: https://status.openai.com
- Support: https://help.openai.com
