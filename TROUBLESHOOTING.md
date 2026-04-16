# NeuralLedger Troubleshooting Guide

## ✅ All Systems Verified Working

All critical fixes have been implemented and tested:

### Fixed Issues
1. ✅ **CORS Configuration** - All responses include proper CORS headers
2. ✅ **Buffer Polyfill** - algosdk works in browser
3. ✅ **WebSocket Connection** - Proper cleanup and reconnection logic
4. ✅ **x402 Payment Flow** - 402 responses handled correctly

---

## Current System Status

Run `./test-system.ps1` to verify all components:

```powershell
./test-system.ps1
```

Expected output:
- ✅ Backend Health: OK
- ✅ CORS Preflight: 200 with headers
- ✅ 402 Response: Includes CORS headers
- ✅ WebSocket: Connected successfully
- ✅ Frontend: Running on port 5174
- ✅ Docker: All services up

---

## Common Issues & Solutions

### Issue: "WebSocket connection failed"

**Symptoms:**
- Console shows: `WebSocket connection to 'ws://localhost:8000/api/agents/ws/activity' failed`
- Happens when clicking on input boxes

**Root Cause:**
- React StrictMode causes double-mounting in development
- WebSocket tries to connect multiple times

**Solution:**
✅ Already fixed in `src/hooks/useAgentActivity.ts`:
- Added `mountedRef` to prevent race conditions
- Added 100ms delay to prevent double-invoke
- Proper cleanup in useEffect return

**Verification:**
1. Open browser at http://localhost:5174
2. Open DevTools Console (F12)
3. Navigate to Marketplace or Agent Dashboard
4. Should see: `[AgentFeed] Connected` (only once or twice max)
5. No error messages

---

### Issue: "CORS policy blocked"

**Symptoms:**
- Console shows: `Access to fetch... has been blocked by CORS policy`
- API calls fail with network error

**Root Cause:**
- Backend not including CORS headers on all responses
- Especially critical for 402 responses

**Solution:**
✅ Already fixed in `backend/middleware/x402_middleware.py`:
- `add_cors_headers()` function adds headers to ALL responses
- OPTIONS preflight passes through correctly
- 402 responses include CORS headers

**Verification:**
```powershell
# Test OPTIONS
$headers = @{'Origin'='http://localhost:5174'}
Invoke-WebRequest -Uri 'http://localhost:8000/api/tasks/run' -Method OPTIONS -Headers $headers

# Should return 200 with Access-Control-Allow-Origin header
```

---

### Issue: "Buffer is not defined"

**Symptoms:**
- Console shows: `Module "buffer" has been externalized`
- algosdk fails to load

**Root Cause:**
- Browser doesn't have Node.js Buffer API
- algosdk requires Buffer for cryptographic operations

**Solution:**
✅ Already fixed in `vite.config.ts`:
- Installed `vite-plugin-node-polyfills`
- Configured Buffer, process, util, stream polyfills
- Added resolve alias for buffer

**Verification:**
1. Check package.json: `"vite-plugin-node-polyfills": "^0.26.0"`
2. Check vite.config.ts: `nodePolyfills()` plugin configured
3. No Buffer errors in console

---

### Issue: Payment modal doesn't appear

**Symptoms:**
- Click "Submit Task" but nothing happens
- No Pera Wallet popup

**Possible Causes:**

1. **Wallet not connected**
   - Solution: Click "Connect Wallet" first
   - Verify wallet address shows in navbar

2. **402 response blocked by CORS**
   - Solution: Already fixed (see CORS section above)
   - Verify with test script

3. **x402Client error**
   - Check console for specific error message
   - Verify `X-Task-Hash` header is being sent

**Verification:**
1. Open DevTools Network tab
2. Submit a task
3. Should see:
   - First request: 402 Payment Required
   - Response includes payment details
   - Modal appears with payment info

---

## Development Workflow

### Starting the System

```bash
# 1. Start Docker services
docker-compose up -d

# 2. Start frontend (if not in Docker)
npm run dev

# 3. Verify all services
./test-system.ps1
```

### Stopping the System

```bash
# Stop Docker services
docker-compose down

# Frontend stops automatically (Ctrl+C if running manually)
```

### Restarting After Code Changes

**Backend changes:**
```bash
docker-compose restart backend
```

**Frontend changes:**
- Vite auto-reloads (no restart needed)
- If issues persist: Refresh browser (Ctrl+Shift+R)

**Middleware changes:**
```bash
# Must restart backend
docker-compose restart backend

# Then refresh browser
```

---

## Testing the Payment Flow

### Manual Task Submission

1. Open http://localhost:5174
2. Connect Pera Wallet
3. Go to "Marketplace" tab
4. Enter a prompt (e.g., "Explain quantum computing")
5. Click "Submit Task"
6. Expected flow:
   - Backend returns 402 Payment Required
   - Modal shows payment details
   - Click "Confirm & Pay"
   - Pera Wallet popup appears
   - Sign transaction
   - Task executes
   - Result appears

### Autonomous Mode

1. Go to "Autonomous Mode" tab
2. Enter a goal (e.g., "Research AI trends")
3. Set budget (e.g., 1 ALGO)
4. Click "Launch Pipeline"
5. Expected flow:
   - Master agent spawns
   - Sub-agents execute tasks
   - Audit trail shows progress
   - Final result appears

---

## Environment Variables

### Required Variables (.env)

```bash
# Backend
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:5174

# Frontend (VITE_ prefix)
VITE_BACKEND_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
VITE_ALGORAND_NODE_URL=https://testnet-api.algonode.cloud

# Algorand
ALGORAND_NODE_URL=https://testnet-api.algonode.cloud
ALGORAND_INDEXER_URL=https://testnet-idx.algonode.cloud
ALGORAND_NETWORK=testnet

# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/neuralledger
REDIS_URL=redis://localhost:6379/0
```

### Optional Variables (for full features)

```bash
# AI Features
OPENAI_API_KEY=sk-...
PINECONE_API_KEY=...

# Storage
WEB3_STORAGE_TOKEN=...

# Smart Contracts (if deployed)
ESCROW_CONTRACT_APP_ID=123456
REPUTATION_CONTRACT_APP_ID=123457
```

---

## Debugging Tips

### Check Backend Logs

```bash
docker logs algo_hack_series-backend-1 -f
```

### Check Frontend Console

1. Open DevTools (F12)
2. Go to Console tab
3. Look for:
   - `[AgentFeed] Connected` - WebSocket working
   - No CORS errors
   - No Buffer errors

### Check Network Requests

1. Open DevTools (F12)
2. Go to Network tab
3. Submit a task
4. Verify:
   - OPTIONS request: 200 OK
   - POST request: 402 Payment Required
   - Headers include `Access-Control-Allow-Origin`

### Test Individual Components

```powershell
# Backend health
curl http://localhost:8000/health

# WebSocket (in browser console)
new WebSocket("ws://localhost:8000/api/agents/ws/activity")

# CORS
./test-system.ps1
```

---

## Known Limitations (Development Mode)

1. **Smart contracts not deployed**
   - Agent registration uses Redis fallback
   - Payment verification simplified
   - Normal for local development

2. **Pinecone not configured**
   - Semantic cache disabled
   - Exact cache still works
   - Optional feature

3. **React StrictMode double-mounting**
   - WebSocket may connect twice in dev
   - Normal React behavior
   - Fixed with proper cleanup

---

## Getting Help

If issues persist:

1. Run `./test-system.ps1` and share output
2. Check browser console for errors
3. Check backend logs: `docker logs algo_hack_series-backend-1`
4. Verify .env file has correct values
5. Try restarting all services: `docker-compose restart`

---

## Success Indicators

You know everything is working when:

✅ Test script shows all green checkmarks
✅ Browser console shows `[AgentFeed] Connected`
✅ No CORS errors in console
✅ No Buffer errors in console
✅ Wallet connects successfully
✅ Payment modal appears when submitting tasks
✅ Pera Wallet popup appears for signing
✅ Tasks execute and return results

---

**Last Updated:** Based on fixes implemented in current session
**System Status:** All critical issues resolved ✅
