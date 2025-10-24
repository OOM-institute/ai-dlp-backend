# Architecture Decision Records (ADR)

## ADR-001: BeautifulSoup over Playwright for Web Crawling

**Status:** Accepted

**Context:**
We need to crawl user-provided websites to extract brand tone, style, and messaging. Two main options were considered:
- BeautifulSoup (static HTML parser)
- Playwright/Puppeteer (headless browser)

**Decision:**
Use BeautifulSoup for this PoC.

**Rationale:**
- **Familiarity**: Most comfortable with BeautifulSoup's API and workflow
- **Simplicity**: BeautifulSoup requires minimal setup (no browser binaries)
- **Speed**: Static parsing is faster than spinning up a headless browser
- **Sufficient for PoC**: Most landing pages have readable HTML structure, JavaScript rendering not critical at this stage
- **Lightweight**: Fewer dependencies and smaller deployment footprint
- **Less complexity**: Reduces moving parts for a proof of concept

**Trade-offs:**
- ❌ **Cannot execute JavaScript**: Modern SPAs (React/Vue/Angular) may not render properly
- ❌ **No dynamic content**: AJAX-loaded content won't be captured
- ✅ **Fast and simple**: Good enough for 80% of websites
- ✅ **Resource efficient**: Lower memory and CPU usage

**Consequences:**
- JavaScript-heavy sites may have incomplete crawling
- For production, we'd add Playwright as a fallback for failed crawls
- Current implementation works well for traditional HTML sites

---

## ADR-002: MongoDB over PostgreSQL for Data Storage

**Status:** Accepted

**Context:**
Need to persist generated page specs, which are JSON-heavy documents with nested sections. Options:
- PostgreSQL (relational with JSONB support)
- MongoDB (document-oriented NoSQL)

**Decision:**
Use MongoDB for this PoC.

**Rationale:**
- **Easy setup**: Quick to install and get running locally
- **Schema flexibility**: Page specs are JSON; MongoDB stores them natively
- **No ORM overhead**: Direct JSON in/out without mapping
- **Rapid prototyping**: No migrations, no schema changes needed
- **Natural fit**: Page spec structure matches document model perfectly

**Trade-offs:**
- ✅ **Fast iteration**: Change page spec structure without migrations
- ✅ **Developer experience**: Simple CRUD operations
- ✅ **Scalability**: Horizontal scaling if needed later

**Consequences:**
- Easy to add/remove fields from page specs during development
- For production with multi-tenancy, we'd add user authentication and references
- Version tracking is simple (increment integer field)

---

## ADR-003: Azure OpenAI with GPT-4o for Generation

**Status:** Accepted

**Context:**
Need an LLM to generate landing page content from user inputs and crawled data. Options:
- OpenAI GPT-4 (via OpenAI API)
- Azure OpenAI GPT-4o (via Azure)
- Open-source models (Llama, Mistral)

**Decision:**
Use Azure OpenAI with GPT-4o model.

**Rationale:**
- **Access**: Already have Azure OpenAI credentials and access
- **Model quality**: GPT-4o is highly capable for creative content generation
- **Structured output**: Good at following JSON schema instructions
- **Enterprise-ready**: Azure provides SLA, security, compliance
- **Reliability**: Stable API with good uptime

**Trade-offs:**
- ❌ **Vendor lock-in**: Tied to Azure ecosystem
- ❌ **Latency**: Several seconds per generation (acceptable for PoC)
- ✅ **Quality**: Excellent copy generation, understands brand tone
- ✅ **JSON compliance**: Rarely fails to return valid JSON

**Consequences:**
- API calls are synchronous; for production, consider async/queue
- Prompt engineering is critical for quality output
- Easy to swap for other providers (OpenAI, Anthropic) via interface layer

---

## Summary

| Decision | Choice | Main Benefit | Main Trade-off |
|----------|--------|--------------|----------------|
| Web Crawler | BeautifulSoup | Familiar, simple, fast | No JS rendering |
| Database | MongoDB | Easy setup, flexible schema | No relational queries |
| LLM Provider | Azure OpenAI GPT-4o | Access + Quality | Latency |

These decisions optimize for **rapid prototyping** and **developer velocity** at the PoC stage. For production, we'd add:
- Playwright fallback for JS-heavy sites
- PostgreSQL for user/team management (if relational data needed)
- Async job queue for LLM calls
- Caching layer for repeated generations
