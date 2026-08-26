with open('backend/app/api/notifications.py', 'r') as f:
    c = f.read()
c = c.replace('from app.api.auth import get_current_user', 'from app.api.deps import get_current_active_user')
c = c.replace('Depends(get_current_user)', 'Depends(get_current_active_user)')
with open('backend/app/api/notifications.py', 'w') as f:
    f.write(c)

with open('backend/app/api/search.py', 'r') as f:
    c = f.read()
c = c.replace('from app.api.auth import get_current_user', 'from app.api.deps import get_current_active_user')
c = c.replace('Depends(get_current_user)', 'Depends(get_current_active_user)')
with open('backend/app/api/search.py', 'w') as f:
    f.write(c)
