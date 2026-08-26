import re

# Fix layout.tsx
with open('frontend/src/app/dashboard/layout.tsx', 'r', encoding='utf-8') as f:
    layout_content = f.read()

layout_content = layout_content.replace('href={/dashboard/businesses/} style={{', 'href={/dashboard/businesses/} style={{')
layout_content = layout_content.replace('href={/dashboard/businesses//inbox?conversation=} style={{', 'href={/dashboard/businesses//inbox?conversation=} style={{')

with open('frontend/src/app/dashboard/layout.tsx', 'w', encoding='utf-8') as f:
    f.write(layout_content)

# Fix notifications/page.tsx
with open('frontend/src/app/dashboard/notifications/page.tsx', 'r', encoding='utf-8') as f:
    notif_content = f.read()

notif_content = notif_content.replace('\Bearer \\', 'Bearer ')
notif_content = notif_content.replace('/api/v1/notifications//read', '/api/v1/notifications//read')

with open('frontend/src/app/dashboard/notifications/page.tsx', 'w', encoding='utf-8') as f:
    f.write(notif_content)

# Fix settings/page.tsx
with open('frontend/src/app/dashboard/settings/page.tsx', 'r', encoding='utf-8') as f:
    settings_content = f.read()

settings_content = settings_content.replace('\Bearer \\', 'Bearer ')
settings_content = settings_content.replace('Error: ', 'Error: ')

with open('frontend/src/app/dashboard/settings/page.tsx', 'w', encoding='utf-8') as f:
    f.write(settings_content)

