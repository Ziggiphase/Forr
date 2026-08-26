import re

with open('frontend/src/app/dashboard/layout.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('<div style={{ display: "flex", height: "100vh", fontFamily: "sans-serif" }}>', '<div style={{ display: "flex", height: "100vh", width: "100vw", fontFamily: "sans-serif" }}>')

with open('frontend/src/app/dashboard/layout.tsx', 'w', encoding='utf-8') as f:
    f.write(content)

with open('frontend/src/app/layout.tsx', 'r', encoding='utf-8') as f:
    content2 = f.read()

content2 = content2.replace('h-full', 'min-h-screen w-full')

with open('frontend/src/app/layout.tsx', 'w', encoding='utf-8') as f:
    f.write(content2)

