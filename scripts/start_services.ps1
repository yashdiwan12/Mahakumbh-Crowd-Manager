# Simple helper to run services locally
param([string]$service = 'backend')
if($service -eq 'backend'){
  Write-Host "Starting backend (uvicorn)"
  uvicorn app.main:app --reload
} elseif ($service -eq 'frontend'){
  Write-Host "Start frontend with: cd frontend; npm run dev"
} else {
  Write-Host "Use 'backend' or 'frontend'"
}
