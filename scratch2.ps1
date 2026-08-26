\ = Get-Content -LiteralPath 'backend/app/services/agent.py' -Raw
\ = \ -replace '\\"\\"\\"', '"""'
Set-Content -Path 'backend/app/services/agent.py' -Value \ -NoNewline
