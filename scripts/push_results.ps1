param(
    [string]$RepoPath = "C:\Users\Paul\oraculo_pitoniso\oraculo-pitoniso-publisher",
    [string]$BotDataPath = "C:\Users\Paul\oraculo_pitoniso\trance-trading-competition\data\competition_results.json",
    [string]$CommitMessage = "Actualizar datos de competencia - $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
)

Write-Host "=== Subiendo datos del bot al publicador ===" -ForegroundColor Green

# Verificar que existe el archivo del bot
if (-not (Test-Path $BotDataPath)) {
    Write-Host "ERROR: No se encuentra $BotDataPath" -ForegroundColor Red
    Write-Host "Buscando archivos de resultados..."
    $found = Get-ChildItem -Path "C:\Users\Paul\oraculo_pitoniso" -Recurse -Filter "*results*.json" | Select-Object -First 5
    if ($found) {
        Write-Host "Archivos encontrados:" -ForegroundColor Yellow
        $found | ForEach-Object { Write-Host "  $($_.FullName)" }
    }
    exit 1
}

# Copiar el archivo
$destino = Join-Path $RepoPath "data\competition_results.json"
Copy-Item -Path $BotDataPath -Destination $destino -Force
Write-Host "Datos copiados a $destino" -ForegroundColor Green

# Ir al repo y hacer commit
Push-Location $RepoPath
try {
    git add data/competition_results.json
    git commit -m $CommitMessage
    git push origin main
    Write-Host "Push exitoso a GitHub!" -ForegroundColor Green
}
catch {
    Write-Host "Error en git: $_" -ForegroundColor Red
    Write-Host "Asegurate de haber hecho git clone primero." -ForegroundColor Yellow
}
finally {
    Pop-Location
}

Write-Host "=== Proceso completado ===" -ForegroundColor Green
