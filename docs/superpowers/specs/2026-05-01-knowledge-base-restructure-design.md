# Knowledge Base Granular Restructuring Design

## Goal
Restructure the Brastel Remit knowledge base into small, topic-specific Markdown files to optimize retrieval and understanding for a 4B parameter LLM agent.

## Architecture
- **Location**: `/knowledge/`
- **Format**: Clean, standard Markdown (no XML tags).
- **Naming**: Descriptive, prefix-based filenames for clear tool/file selection.

## File Taxonomy

### 1. Setup & Registration
- `setup_app_install.md`: Steps for downloading the app on iOS and Android.
- `setup_registration_jp_national.md`: Registration using a Japanese Driver's License.
- `setup_registration_foreign_national.md`: Registration using a Residence Card.
- `setup_registration_my_number.md`: Registration using a My Number Card.
- `setup_document_reupload.md`: How to re-upload documents if rejected.

### 2. Account & Recipients
- `account_recipient_add.md`: How to add a new recipient in the app.

### 3. Financial Operations
- `operation_send_money.md`: Step-by-step instructions for executing a transfer.
- `operation_deposit_jp_bank_card.md`: Depositing at Japan Post Bank with a card.
- `operation_deposit_jp_bank_no_account.md`: Depositing at Japan Post Bank without an account.
- `operation_deposit_mizuho_atm.md`: Depositing at Mizuho Bank ATMs.
- `operation_deposit_lawson_atm.md`: Depositing at Lawson Bank ATMs.
- `operation_deposit_furikomi.md`: General bank transfer instructions.

### 4. FAQ & Specific Knowledge
- `faq_fees_recipient.md`: Information on recipient-side fees in different countries.
- `faq_delivery_brazil_pix.md`: Details on PIX transfer speed for Brazil.
- `service_overview_benefits.md`: High-level benefits (Safety, Licensing, Transparency).
- `service_step_by_step_guide.md`: Simplified 1-2-3 guide for new users.

## Transformation Strategy
1. **Extract**: Parse content from `source_knowledge/*.md`.
2. **Standardize**: Convert XML tags (`<Tutorial>`, etc.) into Markdown headers and lists.
3. **Isolate**: Create individual files for each topic.
4. **Update Index**: Revise `knowledge/knowledge_base.md` to act as an index/manifest of all files.

## Success Criteria
- No XML tags remain in the `/knowledge/` directory.
- Files are under 5KB each (ideal for small LLM context).
- Filenames clearly describe the contents.
