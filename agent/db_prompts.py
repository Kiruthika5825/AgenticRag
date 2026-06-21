SCHEMA_CONTEXT = """
You have access to a PostgreSQL database with the following table:

Table: orders
  - _id          → unique identifier for each order
  - brand_id     → which brand this order belongs to
  - brand_order_id → Shopify's order ID stored for reference
  - customer_id  → the customer who placed this order
  - order_date   → date and time when order was placed
  - base_price   → base price of the order before taxes
  - taxes        → tax applied (IGST or CGST)
  - total_price  → final total price including taxes
  - status       → current status of the order
  - refund_amount → amount refunded for this order
  - is_active    → whether the order is active (boolean)
  - created_by   → who created this record
  - modified_by  → who last modified this record
  - created_at   → when record was created
  - updated_at   → when record was last updated

RULES:
- Only write SELECT queries
- Always use proper PostgreSQL syntax
- Use _id as the primary key when filtering specific orders
"""

SQL_GENERATION_PROMPT = """
{schema}

Convert the following question into a valid PostgreSQL SELECT query.
Return ONLY the SQL query. No explanation. No markdown. No backticks.

Question: {question}
SQL:
"""

SQL_EXPLANATION_PROMPT = """
The user asked: {question}

The database returned these results:
{results}

Explain these results in clear, simple English. Be concise and direct.
"""