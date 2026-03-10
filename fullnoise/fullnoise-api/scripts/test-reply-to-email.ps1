# Test reply-to-email flow (simulated inbound webhook).
# Prereqs: API running, at least one client with that email and a report.
# Usage: .\scripts\test-reply-to-email.ps1 -FromEmail "client@example.com" -Question "Why did costs go up?"

param(
    [Parameter(Mandatory=$true)][string]$FromEmail,
    [Parameter(Mandatory=$true)][string]$Question,
    [string]$BaseUrl = "http://localhost:8000"
)

$body = @{
    from_email = $FromEmail
    subject    = "Report"
    text       = $Question
} | ConvertTo-Json

$resp = Invoke-RestMethod -Uri "$BaseUrl/webhooks/resend/inbound-test" -Method Post -Body $body -ContentType "application/json"
$resp | ConvertTo-Json
