# Microsoft Teams Integration - No Codebase Changes Required

## Overview

Yes! Several elements of your Cranswick Technical Standards Agent can be connected to Microsoft Teams **without modifying your codebase**. Here are the integration options:

## ✅ Integration Options (No Code Changes)

### 1. **Teams Tab App** - Embed Your Web Application
**What it does:** Embed your existing React frontend as a tab in Teams channels or personal app.

**How it works:**
- Package your existing web app as a Teams app
- Users access the full application directly in Teams
- All functionality remains the same (Chat, Documents, Upload, Analytics, Generate)

**Setup Required:**
1. Create a Teams app manifest (`manifest.json`)
2. Deploy your frontend to a public URL (Azure App Service/Container Apps)
3. Register the app in Teams App Studio or Developer Portal
4. Install in Teams

**Benefits:**
- ✅ Zero code changes needed
- ✅ Users access everything in Teams
- ✅ Single Sign-On via Azure AD (if configured)
- ✅ Available in Teams sidebar

**Limitation:** Requires your app to be publicly accessible (not just localhost)

---

### 2. **Power Automate/Logic Apps Integration**
**What it does:** Create workflows that connect Teams actions to your API endpoints.

**Use Cases:**
- **Post to Teams when document is uploaded**
- **Query chat from Teams chat**
- **Notify Teams channel about new documents**
- **Generate reports and post to Teams**

**How it works:**
- Use Power Automate connectors to call your REST API
- Trigger workflows from Teams actions (mentions, messages, etc.)
- Post results back to Teams channels

**Example Flow:**
```
Teams Message → Power Automate → Your API (/api/chat) → Format Response → Post to Teams
```

**Setup Required:**
1. Create Power Automate flow
2. Add "HTTP" connector to call your API
3. Add Teams connector for input/output
4. Configure authentication (API keys)

**Benefits:**
- ✅ No code changes
- ✅ Visual workflow builder
- ✅ Can trigger from Teams chat, channels, mentions
- ✅ Can post formatted responses

---

### 3. **Teams Bot Framework** (Azure Bot Service)
**What it does:** Create a chatbot that queries your API and responds in Teams.

**How it works:**
- Deploy Azure Bot Service (no code needed - can use Power Virtual Agents)
- Configure bot to call your `/api/chat` endpoint
- Users chat with bot in Teams, bot queries your RAG system
- Bot formats responses in Teams

**Setup Options:**

**Option A: Power Virtual Agents (No-code)**
1. Create bot in Power Virtual Agents
2. Add API call to your `/api/chat` endpoint
3. Publish to Teams

**Option B: Azure Bot Framework (Low-code)**
1. Deploy bot template
2. Configure messaging endpoint to proxy to your API
3. Register bot in Teams

**Benefits:**
- ✅ Natural language queries in Teams
- ✅ Can use Power Virtual Agents (no coding)
- ✅ Integrates with your existing chat API
- ✅ Works in Teams chat, channels, personal chats

---

### 4. **Teams Webhooks (Incoming Webhooks)**
**What it does:** Send notifications from your backend to Teams channels.

**Use Cases:**
- Notify Teams when new documents are uploaded
- Send analytics reports to Teams
- Alert when documents are deleted/updated
- Daily/weekly summaries

**How it works:**
- Create Incoming Webhook in Teams channel
- Call webhook URL from external service/Power Automate
- Messages appear in Teams channel

**Setup Required:**
1. Create Incoming Webhook in Teams channel
2. Get webhook URL
3. Use Power Automate or Azure Logic Apps to call webhook
4. Optionally set up scheduled triggers

**Benefits:**
- ✅ Simple setup (just a URL)
- ✅ No code changes needed
- ✅ Can be triggered by Power Automate/Logic Apps
- ✅ Rich message formatting (Adaptive Cards)

---

### 5. **SharePoint/OneDrive Integration**
**What it does:** Access documents stored in SharePoint/OneDrive via Teams.

**Current State:**
- Your documents are in Azure Blob Storage
- Teams can access SharePoint/OneDrive files natively

**Potential Integration:**
- **Option A:** Use SharePoint/OneDrive as document source
  - Upload documents to SharePoint/OneDrive
  - Teams users can see files in Teams Files tab
  - Your system could watch SharePoint for new files (via Power Automate)

**Option B:** Sync Azure Blob Storage to SharePoint (via Power Automate)

**Benefits:**
- ✅ Native Teams file access
- ✅ Version control in SharePoint
- ✅ Co-authoring capabilities
- ✅ Teams Files tab integration

---

### 6. **Teams Adaptive Cards**
**What it does:** Send rich, interactive cards to Teams channels or chats.

**Use Cases:**
- Document cards showing preview/metadata
- Interactive query forms
- Analytics dashboard cards
- Approval workflows for document updates

**How it works:**
- Generate Adaptive Card JSON
- Send via webhook or bot
- Cards appear as rich messages in Teams

**Setup Required:**
- Configure webhook/bot to send Adaptive Card format
- Design card layout (can be done in Power Automate)

**Benefits:**
- ✅ Rich, interactive UI in Teams
- ✅ Buttons, forms, images
- ✅ Can trigger actions back to your API
- ✅ Professional appearance

---

## 🔧 Quick Start Examples

### Example 1: Embed as Teams Tab

1. **Deploy frontend to Azure:**
   ```bash
   # Deploy to Azure App Service or Container Apps
   az webapp up --name your-app-name --runtime "NODE:20-lts"
   ```

2. **Create Teams manifest:**
   ```json
   {
     "manifestVersion": "1.16",
     "version": "1.0.0",
     "id": "your-app-id",
     "packageName": "com.cranswick.techstandards",
     "developer": {
       "name": "Cranswick",
       "websiteUrl": "https://your-app.azurewebsites.net",
       "privacyUrl": "https://your-app.azurewebsites.net/privacy",
       "termsOfUseUrl": "https://your-app.azurewebsites.net/terms"
     },
     "icons": {
       "color": "icon-color.png",
       "outline": "icon-outline.png"
     },
     "name": {
       "short": "Tech Standards",
       "full": "Cranswick Technical Standards Agent"
     },
     "description": {
       "short": "AI-powered technical standards",
       "full": "Access and query technical standards documents with AI assistance"
     },
     "accentColor": "#0078D4",
     "staticTabs": [
       {
         "entityId": "index",
         "name": "Technical Standards",
         "contentUrl": "https://your-app.azurewebsites.net",
         "websiteUrl": "https://your-app.azurewebsites.net",
         "scopes": ["personal", "team"]
       }
     ],
     "permissions": ["identity", "messageTeamMembers"],
     "validDomains": ["your-app.azurewebsites.net"]
   }
   ```

3. **Upload manifest to Teams:**
   - Teams → Apps → Upload a custom app
   - Select your manifest.zip

---

### Example 2: Power Automate - Chat Query Bot

**Flow Steps:**
1. **Trigger:** When a message is posted in a Teams channel
2. **Condition:** Check if message mentions bot or contains keyword
3. **HTTP Request:** POST to `https://your-api.azurewebsites.net/api/chat`
   - Body: `{"query": "Teams message text"}`
   - Headers: `Authorization: Bearer YOUR_API_KEY`
4. **Parse JSON:** Extract response from API
5. **Post Message:** Reply to Teams channel with AI response

**No code changes needed** - all done in Power Automate UI!

---

### Example 3: Webhook Notifications

**Setup:**
1. Teams channel → Connectors → Incoming Webhook
2. Copy webhook URL
3. Create Power Automate flow:
   - Trigger: When HTTP request received (or scheduled)
   - Action: HTTP POST to Teams webhook URL
   - Body: Formatted message with document info

**Use cases:**
- Daily document upload summary
- New document notifications
- Weekly analytics report

---

## 📋 Integration Checklist

### For Teams Tab:
- [ ] Deploy frontend to public URL (Azure App Service/Container Apps)
- [ ] Configure CORS to allow Teams domain (`*.teams.microsoft.com`)
- [ ] Create Teams app manifest
- [ ] Test SSO (Azure AD integration)
- [ ] Upload and install app in Teams

### For Power Automate:
- [ ] Create Power Automate account
- [ ] Get API key/authentication method for your backend
- [ ] Design workflow
- [ ] Test API connectivity
- [ ] Publish flow

### For Bot:
- [ ] Create Azure Bot Service or Power Virtual Agents bot
- [ ] Configure messaging endpoint
- [ ] Connect to your `/api/chat` endpoint
- [ ] Register bot in Teams
- [ ] Test in Teams

### For Webhooks:
- [ ] Create Incoming Webhook in Teams
- [ ] Create Power Automate flow to send messages
- [ ] Design message format (Adaptive Cards)
- [ ] Test webhook URL

---

## 🔐 Security Considerations

### Authentication:
- **Current:** Your API likely uses API keys
- **Teams Option:** Can use Azure AD SSO
- **Recommendation:** Configure Azure AD authentication in your backend (minimal code changes)

### CORS:
- Add Teams domains to your CORS configuration:
  ```python
  cors_origins = [
      "https://teams.microsoft.com",
      "https://*.teams.microsoft.com",
      "https://*.microsoft.com"
  ]
  ```

### API Security:
- Use API keys or Azure AD tokens
- Rate limiting
- IP whitelisting (if needed)

---

## 💰 Cost Considerations

### Free Options:
- ✅ Power Automate: Free tier (750 actions/month)
- ✅ Teams Apps: Free to create and deploy
- ✅ Incoming Webhooks: Free
- ✅ Power Virtual Agents: Free tier (2,000 messages/month)

### Paid Options (if you exceed free tiers):
- Power Automate Premium: ~$15/user/month
- Azure Bot Service: Pay-per-use (very low cost)
- Power Virtual Agents: ~$200/month for higher limits

---

## 🚀 Recommended Starting Point

**Easiest to implement (no code changes):**

1. **Start with Incoming Webhooks** - 5 minutes setup
   - Get notifications about document changes
   - Post analytics to Teams

2. **Add Power Automate Flow** - 15 minutes
   - Query your chat API from Teams
   - Post responses back to Teams

3. **Deploy as Teams Tab** - 30 minutes
   - Embed full application in Teams
   - Users access everything in one place

---

## 📚 Additional Resources

- [Teams App Development Docs](https://docs.microsoft.com/en-us/microsoftteams/platform/)
- [Power Automate Connectors](https://docs.microsoft.com/en-us/power-automate/)
- [Teams Adaptive Cards](https://adaptivecards.io/)
- [Power Virtual Agents](https://powervirtualagents.microsoft.com/)

---

## ✅ Summary

**Yes, you can connect to Teams without codebase changes using:**
1. ✅ Teams Tab (embed web app)
2. ✅ Power Automate (API integration)
3. ✅ Teams Bot (Power Virtual Agents or Azure Bot)
4. ✅ Webhooks (notifications)
5. ✅ Adaptive Cards (rich messages)

The **easiest approach** is to start with **Power Automate** to create workflows that call your existing API endpoints, then optionally deploy as a **Teams Tab** for full integration.
