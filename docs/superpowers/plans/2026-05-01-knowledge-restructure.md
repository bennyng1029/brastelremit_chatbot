# Knowledge Base Restructuring Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Convert 3 source files into 15+ granular, clean Markdown files in the `knowledge/` directory and verify them.

**Architecture:** Use subagents to perform extraction and transformation from XML-like source markdown to clean, standard markdown.

**Tech Stack:** Markdown, Python (for potential batch scripts), Ripgrep (for finding sections).

---

### Task 1: Setup and App Installation Guides
**Files:**
- Create: `knowledge/setup_app_install.md`
- Source: `source_knowledge/Brastel Remit Chatbot DalAi - tutorial.md`

- [ ] **Step 1: Extract "HOW TO DOWNLOAD" sections for iOS and Android**
- [ ] **Step 2: Format as clean Markdown (H1, H2, Numbered list)**
- [ ] **Step 3: Save to `knowledge/setup_app_install.md`**

---

### Task 2: Registration and Document Submission Guides
**Files:**
- Create: `knowledge/setup_registration_jp_national.md`, `knowledge/setup_registration_foreign_national.md`, `knowledge/setup_registration_my_number.md`, `knowledge/setup_document_reupload.md`
- Source: `source_knowledge/Brastel Remit Chatbot DalAi - tutorial.md`

- [ ] **Step 1: Extract and convert "HOW TO SIGN UP" sections**
- [ ] **Step 2: Extract and convert "HOW TO RE-UPLOAD DOCUMENTS"**
- [ ] **Step 3: Save each to their respective files**

---

### Task 3: Account and Transfer Operations
**Files:**
- Create: `knowledge/account_recipient_add.md`, `knowledge/operation_send_money.md`
- Source: `source_knowledge/Brastel Remit Chatbot DalAi - tutorial.md`

- [ ] **Step 1: Extract and convert "HOW TO ADD A RECIPIENT" and "HOW TO SEND MONEY"**
- [ ] **Step 2: Save to respective files**

---

### Task 4: Deposit Operations (Granular ATM Guides)
**Files:**
- Create: `knowledge/operation_deposit_jp_bank_card.md`, `knowledge/operation_deposit_jp_bank_no_account.md`, `knowledge/operation_deposit_mizuho_atm.md`, `knowledge/operation_deposit_lawson_atm.md`, `knowledge/operation_deposit_furikomi.md`
- Source: `source_knowledge/Brastel Remit Chatbot DalAi - tutorial.md`

- [ ] **Step 1: Extract and convert specific ATM procedures**
- [ ] **Step 2: Save to respective files**

---

### Task 5: FAQs and Service Overview
**Files:**
- Create: `knowledge/faq_fees_recipient.md`, `knowledge/faq_delivery_brazil_pix.md`, `knowledge/service_overview_benefits.md`, `knowledge/service_step_by_step_guide.md`
- Source: `source_knowledge/Brastel Remit - Answer patterns.md`, `source_knowledge/Brastel Remit- AI Chatbot learning doc.md`

- [ ] **Step 1: Extract Q&A and general info**
- [ ] **Step 2: Save to respective files**

---

### Task 6: Knowledge Base Index and Verification
**Files:**
- Modify: `knowledge/knowledge_base.md`

- [ ] **Step 1: Update `knowledge_base.md` to list all new files as an index**
- [ ] **Step 2: Run a final subagent check to verify content accuracy across all files**
