# Sends a report email TO YOU so you can reply and test the reply-to-email flow.
#
# Prereqs:
# - API running (uvicorn) on $BaseUrl
# - Worker running (arq app.worker.WorkerSettings) so the report is actually sent
# - .env has ADMIN_EMAIL, ADMIN_PASSWORD, RESEND_API_KEY, RESEND_FROM_EMAIL, OPENAI_API_KEY
#
# Usage: .\scripts\send-me-a-report.ps1 -MyEmail "you@example.com"
#        .\scripts\send-me-a-report.ps1 -MyEmail "you@example.com" -BaseUrl "http://localhost:8000"

param(
    [Parameter(Mandatory=$true)][string]$MyEmail,
    [string]$BaseUrl = "http://localhost:8000",
    [string]$AdminEmail = "admin@fullnoise.ai",
    [string]$AdminPassword = "admin"
)

$ErrorActionPreference = "Stop"

# 1) Admin login
Write-Host "Logging in as admin..." -ForegroundColor Cyan
$loginBody = @{ email = $AdminEmail; password = $AdminPassword } | ConvertTo-Json
$loginResp = Invoke-RestMethod -Uri "$BaseUrl/auth/admin-login" -Method Post -Body $loginBody -ContentType "application/json"
$token = $loginResp.token
if (-not $token) { Write-Host "Admin login failed." -ForegroundColor Red; exit 1 }

# 2) Create or find client with your email
Write-Host "Getting or creating client for $MyEmail..." -ForegroundColor Cyan
$headers = @{ Authorization = "Bearer $token" }
$clientsResp = Invoke-RestMethod -Uri "$BaseUrl/clients" -Headers $headers -Method Get
$existing = $clientsResp.clients | Where-Object { $_.email -eq $MyEmail.Trim().ToLower() }
$clientId = $null
if ($existing) {
    $clientId = $existing.id
    Write-Host "  Client already exists (id: $clientId)." -ForegroundColor Gray
} else {
    $createBody = @{ name = "Test User"; email = $MyEmail.Trim().ToLower() } | ConvertTo-Json
    $createResp = Invoke-RestMethod -Uri "$BaseUrl/clients" -Method Post -Headers $headers -Body $createBody -ContentType "application/json"
    $clientId = $createResp.id
    Write-Host "  Created client (id: $clientId)." -ForegroundColor Gray
}

# 3) Queue send-report (worker will send the email)
Write-Host "Queuing report send (worker must be running)..." -ForegroundColor Cyan
$reportBody = @{ client_id = $clientId } | ConvertTo-Json
Invoke-RestMethod -Uri "$BaseUrl/send-report" -Method Post -Headers $headers -Body $reportBody -ContentType "application/json" | Out-Null

Write-Host ""
Write-Host "Done. Check the inbox for: $MyEmail" -ForegroundColor Green
Write-Host "  - If the worker is running, the report email should arrive in a few seconds." -ForegroundColor Gray
Write-Host "  - Reply to that email with any question (e.g. 'Why did costs go up?')." -ForegroundColor Gray
Write-Host "  - You should get an answer back by email (Resend must have your webhook URL set and your API must be reachable from the internet)." -ForegroundColor Gray
Write-Host ""
