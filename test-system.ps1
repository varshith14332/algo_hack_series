#!/usr/bin/env pwsh
# System Integration Test Script

Write-Host "=== NeuralLedger System Test ===" -ForegroundColor Cyan
Write-Host ""

# Test 1: Backend Health
Write-Host "1. Testing Backend Health..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method GET
    if ($health.status -eq "ok") {
        Write-Host "   ✅ Backend is healthy" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Backend returned unexpected status" -ForegroundColor Red
    }
} catch {
    Write-Host "   ❌ Backend not responding" -ForegroundColor Red
}

# Test 2: CORS Preflight
Write-Host "2. Testing CORS Preflight..." -ForegroundColor Yellow
try {
    $headers = @{
        'Origin' = 'http://localhost:5174'
        'Access-Control-Request-Method' = 'POST'
        'Access-Control-Request-Headers' = 'X-Task-Hash,X-Wallet-Address'
    }
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/tasks/run" -Method OPTIONS -Headers $headers -UseBasicParsing
    $corsOrigin = $response.Headers['Access-Control-Allow-Origin']
    
    if ($response.StatusCode -eq 200 -and $corsOrigin) {
        Write-Host "   ✅ CORS preflight working (Status: $($response.StatusCode), Origin: $corsOrigin)" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  CORS preflight returned $($response.StatusCode)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   ❌ CORS preflight failed" -ForegroundColor Red
}

# Test 3: 402 Payment Required with CORS
Write-Host "3. Testing 402 Response with CORS..." -ForegroundColor Yellow
try {
    $headers = @{
        'Origin' = 'http://localhost:5174'
        'X-Task-Hash' = 'test-hash-123'
        'X-Wallet-Address' = 'TEST'
    }
    Invoke-WebRequest -Uri "http://localhost:8000/api/tasks/run" -Method POST -Headers $headers -UseBasicParsing -ErrorAction Stop
} catch {
    $response = $_.Exception.Response
    if ($response.StatusCode -eq 402) {
        $corsOrigin = $response.Headers['Access-Control-Allow-Origin']
        if ($corsOrigin) {
            Write-Host "   ✅ 402 response includes CORS headers (Origin: $corsOrigin)" -ForegroundColor Green
        } else {
            Write-Host "   ❌ 402 response missing CORS headers" -ForegroundColor Red
        }
    } else {
        Write-Host "   ⚠️  Unexpected status: $($response.StatusCode)" -ForegroundColor Yellow
    }
}

# Test 4: WebSocket Connection
Write-Host "4. Testing WebSocket Connection..." -ForegroundColor Yellow
try {
    $ws = New-Object System.Net.WebSockets.ClientWebSocket
    $cts = New-Object System.Threading.CancellationTokenSource
    $uri = [System.Uri]::new("ws://localhost:8000/api/agents/ws/activity")
    $task = $ws.ConnectAsync($uri, $cts.Token)
    $task.Wait(5000)
    
    if ($ws.State -eq 'Open') {
        Write-Host "   ✅ WebSocket connected successfully" -ForegroundColor Green
        $ws.CloseAsync([System.Net.WebSockets.WebSocketCloseStatus]::NormalClosure, "test", $cts.Token).Wait(1000)
    } else {
        Write-Host "   ❌ WebSocket connection failed: $($ws.State)" -ForegroundColor Red
    }
    
    $ws.Dispose()
    $cts.Dispose()
} catch {
    Write-Host "   ❌ WebSocket error: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 5: Frontend Port
Write-Host "5. Testing Frontend..." -ForegroundColor Yellow
try {
    $connection = Test-NetConnection -ComputerName localhost -Port 5174 -InformationLevel Quiet -WarningAction SilentlyContinue
    if ($connection) {
        Write-Host "   ✅ Frontend running on http://localhost:5174" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Frontend not accessible on port 5174" -ForegroundColor Red
    }
} catch {
    Write-Host "   ❌ Cannot test frontend port" -ForegroundColor Red
}

# Test 6: Docker Services
Write-Host "6. Testing Docker Services..." -ForegroundColor Yellow
$services = docker ps --format "{{.Names}}" | Select-String -Pattern "algo_hack"
if ($services) {
    Write-Host "   ✅ Docker services running:" -ForegroundColor Green
    $services | ForEach-Object { Write-Host "      - $_" -ForegroundColor Gray }
} else {
    Write-Host "   ❌ No Docker services found" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== Test Complete ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "1. Open browser at http://localhost:5174" -ForegroundColor White
Write-Host "2. Open DevTools Console (F12)" -ForegroundColor White
Write-Host "3. Connect Pera Wallet" -ForegroundColor White
Write-Host "4. Try submitting a task" -ForegroundColor White
Write-Host ""
