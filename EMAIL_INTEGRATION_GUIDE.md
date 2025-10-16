# Email Integration & Lead Management System

## Overview

Your ERP system now has a complete **Lead Management** and **Email Integration** system that allows you to capture sales inquiries from emails and convert them into customers and sales orders.

---

## 🎯 Features Implemented

### 1. **Lead Management**
- ✅ Track sales inquiries from multiple sources (email, website, phone, etc.)
- ✅ Assign leads to team members
- ✅ Add notes and follow-up activities
- ✅ Convert leads to customers
- ✅ Automatically create sales orders from leads
- ✅ Track lead status through the sales pipeline

### 2. **Email Inquiry Processing**
- ✅ Receive emails via webhook
- ✅ Store raw email data
- ✅ Process emails into leads
- ✅ Mark spam emails
- ✅ Track email threads

### 3. **Sales Pipeline**
```
Email Inquiry → Lead → Customer → Sales Order → Invoice
```

---

## 📊 Database Models

### Lead Model
Stores sales inquiries with the following information:
- **Contact**: Name, email, phone, company
- **Details**: Subject, message, priority, status
- **Source**: Email, website, phone, referral, etc.
- **Assignment**: Assigned user, follow-up dates
- **Conversion**: Links to customer and sales order

**Lead Statuses:**
- New
- Contacted
- Qualified
- Proposal Sent
- Negotiation
- Won
- Lost

### EmailInquiry Model
Stores raw email data before processing:
- Email sender information
- Subject and body
- Attachments
- Processing status
- Links to created leads

---

## 🚀 How to Use

### Access the System

1. **View All Leads**
   - URL: `/erp/leads/`
   - Filter by status, source, priority, or assigned user
   - Search by name, email, company, or subject

2. **View Email Inquiries**
   - URL: `/erp/email-inquiries/`
   - See all incoming email inquiries
   - Process them into leads or mark as spam

### Creating a Lead Manually

1. Go to `/erp/leads/create/`
2. Fill in contact information
3. Add inquiry details
4. Select source (email, website, phone, etc.)
5. Set priority and status
6. Optionally assign to a user
7. Click "Create Lead"

### Processing Email Inquiries

1. Go to `/erp/email-inquiries/`
2. Click on an inquiry to view details
3. Click "Process to Lead" to convert it
4. Or click "Mark as Spam" to filter it out

### Converting Leads to Customers

1. Open a lead detail page
2. Click "Convert to Customer"
3. Optionally create a sales order automatically
4. The lead status changes to "Won"

---

## 🔗 Email Integration Methods

### Method 1: API Webhook (Recommended)

Your ERP has a webhook endpoint that can receive emails from services like:
- **SendGrid**
- **Mailgun**
- **Zapier**
- **Make.com**
- **Integromat**

**Webhook URL:**
```
POST http://your-domain.com/erp/api/webhook/email/
```

**Payload Format:**
```json
{
  "from_email": "customer@example.com",
  "from_name": "John Doe",
  "subject": "Product Inquiry",
  "body": "I'm interested in your products...",
  "body_html": "<p>I'm interested...</p>",
  "message_id": "unique-message-id",
  "received_at": "2025-10-13T10:30:00Z",
  "attachments": []
}
```

### Method 2: Email Forwarding with Zapier

**Setup Steps:**

1. **Create a Zapier Account** (zapier.com)

2. **Create a New Zap:**
   - Trigger: "Email by Zapier" or "Gmail"
   - Action: "Webhooks by Zapier" - POST

3. **Configure the Trigger:**
   - Set up a mailbox (e.g., sales@yourcompany.com)
   - Forward emails to the Zapier email address

4. **Configure the Action:**
   - URL: `http://your-erp-domain.com/erp/api/webhook/email/`
   - Payload Type: JSON
   - Data:
     ```json
     {
       "from_email": "{{from_email}}",
       "from_name": "{{from_name}}",
       "subject": "{{subject}}",
       "body": "{{body_plain}}",
       "body_html": "{{body_html}}",
       "message_id": "{{message_id}}",
       "received_at": "{{received_at}}"
     }
     ```

5. **Test and Activate**

### Method 3: Email Parsing Services

Use services like:
- **Mailgun Parse API**
- **SendGrid Inbound Parse**
- **CloudMailin**

These can be configured to forward parsed emails to your webhook.

### Method 4: Direct IMAP Integration (Advanced)

For direct email monitoring, you can create a Django management command that:
1. Connects to your email server via IMAP
2. Fetches new emails
3. Creates EmailInquiry records
4. Marks emails as processed

---

## 📋 Workflow Examples

### Example 1: Email to Sale

1. **Customer sends email** to sales@yourcompany.com
2. **Email forwarded** to ERP via Zapier webhook
3. **EmailInquiry created** with status "pending"
4. **Sales team reviews** in `/erp/email-inquiries/`
5. **Process to Lead** - creates Lead record
6. **Sales rep adds notes**, sets follow-up
7. **Convert to Customer** - creates Customer record
8. **Create Sales Order** - generates sales order
9. **Add items** and confirm order
10. **Invoice generated** automatically

### Example 2: Lead Management

1. **Lead comes in** from website form or phone
2. **Create lead manually** at `/erp/leads/create/`
3. **Assign to sales rep**
4. **Add notes** about calls and emails
5. **Update status** through pipeline
6. **Convert when qualified**

---

## 🎨 Admin Interface

Access the Django admin at `/admin/` to:
- View all leads and email inquiries
- Bulk update lead statuses
- Export lead data
- Manage assignments

---

## 🔒 Security Notes

1. **Webhook Authentication**: Currently, the webhook is open. Consider adding:
   - API key authentication
   - IP whitelist
   - HMAC signature verification

2. **Spam Protection**: The system includes spam marking, but consider:
   - Automated spam detection
   - Email validation
   - Rate limiting

---

## 📈 Reports & Analytics

The lead system tracks:
- Total leads
- Leads by status (new, qualified, won, lost)
- Leads by source
- Conversion rates
- Lead response times

---

## 🛠️ Customization

### Add Custom Lead Sources

Edit `erpdb/models.py`:
```python
SOURCE_CHOICES = [
    ('email', 'Email Inquiry'),
    ('website', 'Website Form'),
    ('phone', 'Phone Call'),
    ('referral', 'Referral'),
    ('social_media', 'Social Media'),
    ('trade_show', 'Trade Show'),
    ('webinar', 'Webinar'),  # Add new source
    ('other', 'Other'),
]
```

### Add Custom Lead Fields

You can extend the Lead model with additional fields like:
- Industry
- Company size
- Budget range
- Expected close date

---

## 🧪 Testing the Webhook

### Using cURL:
```bash
curl -X POST http://localhost:8000/erp/api/webhook/email/ \
  -H "Content-Type: application/json" \
  -d '{
    "from_email": "test@example.com",
    "from_name": "Test Customer",
    "subject": "Product Inquiry",
    "body": "I would like to know more about your products.",
    "received_at": "2025-10-13T10:30:00Z"
  }'
```

### Using Postman:
1. Create new POST request
2. URL: `http://localhost:8000/erp/api/webhook/email/`
3. Body type: JSON
4. Add the JSON payload above
5. Send

---

## 📞 Support & Next Steps

### Immediate Actions:
1. ✅ **Database migrations applied** - Lead tables created
2. ✅ **Admin registered** - Access leads in Django admin
3. ✅ **Views and URLs configured** - Access at `/erp/leads/`
4. ⏳ **Create templates** - Need to build frontend templates
5. ⏳ **Set up email forwarding** - Configure Zapier or similar

### Templates Needed:
- `templates/erp/leads/lead_list.html`
- `templates/erp/leads/lead_detail.html`
- `templates/erp/leads/lead_form.html`
- `templates/erp/leads/lead_convert.html`
- `templates/erp/leads/email_inquiry_list.html`
- `templates/erp/leads/email_inquiry_detail.html`

---

## 💡 Integration Examples

### Zapier Integration
- Trigger: Gmail (New Email)
- Filter: Subject contains "inquiry" or "quote"
- Action: POST to webhook
- Result: Automatic lead creation

### Website Form
- Create contact form on your website
- On submit, POST to webhook endpoint
- Automatically creates lead in ERP

### SendGrid Inbound Parse
- Configure domain (e.g., leads@yourcompany.com)
- Set webhook URL
- All emails to that address become leads

---

## 🎉 Benefits

✅ **Centralized Lead Management** - All inquiries in one place
✅ **Automated Lead Capture** - No manual data entry
✅ **Sales Pipeline Tracking** - See where each lead stands
✅ **Email Thread History** - Keep original emails attached
✅ **Conversion Tracking** - From lead to customer to sale
✅ **Team Collaboration** - Assign and track follow-ups
✅ **Integration Ready** - Works with major email services

---

Your ERP system is now ready to receive and manage sales inquiries from email and other sources!

