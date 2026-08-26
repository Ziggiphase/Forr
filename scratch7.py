with open('backend/app/services/paystack.py', 'r') as f:
    c = f.read()
c = c.replace('\\"\\"\\"', '"""')
with open('backend/app/services/paystack.py', 'w') as f:
    f.write(c)
