with open('backend/app/services/agent.py', 'r', encoding='utf-8') as f:
    content = f.read()

old_limit = '''        limit = business.conversation_limit
        if usage >= limit:'''

new_limit = '''        tier = subscription.plan_tier if subscription else "free"
        limit = 50
        if tier == "pro":
            limit = 500
        elif tier == "premium":
            limit = 5000
        
        if usage >= limit:'''

if old_limit in content:
    content = content.replace(old_limit, new_limit)
    with open('backend/app/services/agent.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Replaced limit logic!")
else:
    print("Not found!")
