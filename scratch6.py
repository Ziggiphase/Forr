import re

with open('backend/app/services/inbox.py', 'r') as f:
    content = f.read()

# ai_response, should_escalate, is_resolved, limit_reached, total_tokens = await generate_agent_response(business_id, content)
old_line = "generate_agent_response(business_id, content)"
new_line = "generate_agent_response(business_id, content, conversation.id, conversation.customer_identifier)"

content = content.replace(old_line, new_line)

with open('backend/app/services/inbox.py', 'w') as f:
    f.write(content)
