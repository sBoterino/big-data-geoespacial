<#
F8 — Ejecuta UNA corrida del benchmark y la registra en benchmark/resultados.csv.

Mientras corre el benchmark, muestrea `docker stats` de los contenedores del motor y guarda
el pico de memoria (suma de scheduler/master y workers) y el CPU promedio.

Uso (desde la raíz del repositorio, en PowerShell):
  .\benchmark\medir.ps1 -Motor dask  -Config A -Repeticion 1
  .\benchmark\medir.ps1 -Motor spark -Config B -Repeticion 0   # 0 = calentamiento
  .\benchmark\medir.ps1 -Motor dask  -Config A -Repeticion 1 -Replicas 10   # ~17 M de filas

Config A = 1 worker x 2 núcleos ; Config B = 2 workers x 2 núcleos.
Antes de cada configuración hay que dejar levantados los workers correctos (ver benchmark/README.md).
#>
param(
    [Parameter(Mandatory = $true)][ValidateSet("dask", "spark")][string]$Motor,
    [Parameter(Mandatory = $true)][ValidateSet("A", "B")][string]$Config,
    [Parameter(Mandatory = $true)][int]$Repeticion,
    [int]$Replicas = 1   # 10 = lee /data/parquet/eventos_x10, copia física ×10 (D18)
)
# "Continue": Spark y Dask escriben sus logs por stderr; con "Stop", PowerShell 5.1 los
# trataría como errores y cortaría la corrida.
$ErrorActionPreference = "Continue"
$raiz = Split-Path -Parent $PSScriptRoot
Set-Location $raiz

$workers = if ($Config -eq "A") { 1 } else { 2 }
$ruta = if ($Replicas -gt 1) { "/data/parquet/eventos_x$Replicas" } else { "/data/parquet/eventos" }
$contenedores = if ($Motor -eq "dask") {
    @("bdgeo-dask-scheduler-1", "bdgeo-dask-worker-1-1", "bdgeo-dask-worker-2-1")
} else {
    @("bdgeo-spark-master-1", "bdgeo-spark-worker-1", "bdgeo-spark-worker-2-1")
}

# --- Muestreo de memoria y CPU en segundo plano ---------------------------------------------
$muestras = Join-Path $env:TEMP "bdgeo_stats_$Motor$Config$Repeticion$Replicas.csv"
if (Test-Path $muestras) { Remove-Item $muestras }
# El cliente de Dask corre en un contenedor temporal (bdgeo-dask-job-run-…); se suma igual
# que el driver de Spark, que corre dentro de spark-master.
$prefijoCliente = if ($Motor -eq "dask") { "bdgeo-dask-job-run" } else { "-ninguno-" }
$muestreo = Start-Job -ArgumentList $contenedores, $muestras, $prefijoCliente -ScriptBlock {
    param($nombres, $archivo, $prefijo)
    $i = 0
    while ($true) {
        $lineas = docker stats --no-stream --format "{{.Name}};{{.MemUsage}};{{.CPUPerc}}" 2>$null
        foreach ($l in $lineas) {
            $p = $l -split ";"
            if ($nombres -contains $p[0] -or $p[0].StartsWith($prefijo)) { Add-Content $archivo "$i;$l" }
        }
        $i++
    }
}

function A-MiB([string]$texto) {
    # "512.3MiB / 2GiB" -> 512.3
    $uso = ($texto -split "/")[0].Trim()
    if ($uso -match "^([\d\.]+)\s*([KMG]i?B|B)$") {
        $v = [double]::Parse($matches[1], [Globalization.CultureInfo]::InvariantCulture)
        switch -regex ($matches[2]) {
            "^G" { return $v * 1024 }
            "^M" { return $v }
            "^K" { return $v / 1024 }
            default { return $v / 1MB }
        }
    }
    return 0
}

# --- Ejecución del benchmark ----------------------------------------------------------------
Start-Sleep -Seconds 2   # muestras de referencia antes de empezar
if ($Motor -eq "dask") {
    $salida = docker compose run --rm -v "${raiz}\benchmark:/opt/bench" dask-job `
        python /opt/bench/bench_dask.py --workers $workers --ruta $ruta 2>&1
} else {
    # Solo el driver necesita el script; /tmp es escribible por el usuario "spark" de la imagen.
    docker compose cp benchmark/bench_spark.py spark-master:/tmp/bench_spark.py | Out-Null
    $salida = docker compose exec -T spark-master /opt/spark/bin/spark-submit `
        /tmp/bench_spark.py --workers $workers --ruta $ruta 2>&1
}
Start-Sleep -Seconds 2
Stop-Job $muestreo; Remove-Job $muestreo

$linea = $salida | Where-Object { "$_" -like "RESULTADO_BENCH *" } | Select-Object -Last 1
if (-not $linea) {
    $salida | Select-Object -Last 30 | ForEach-Object { Write-Host $_ }
    throw "El benchmark no imprimió RESULTADO_BENCH (ver la salida de arriba)."
}
$r = ("$linea" -replace "^RESULTADO_BENCH ", "") | ConvertFrom-Json

# --- Pico de memoria y CPU promedio ---------------------------------------------------------
$memPico = 0.0; $cpuSuma = 0.0; $n = 0
if (Test-Path $muestras) {
    $porMuestra = Get-Content $muestras | ForEach-Object {
        $p = $_ -split ";"
        [pscustomobject]@{
            i   = [int]$p[0]
            mem = A-MiB $p[2]
            cpu = [double]::Parse(($p[3] -replace "%", ""), [Globalization.CultureInfo]::InvariantCulture)
        }
    } | Group-Object i
    foreach ($g in $porMuestra) {
        $mem = ($g.Group | Measure-Object mem -Sum).Sum
        $cpu = ($g.Group | Measure-Object cpu -Sum).Sum
        if ($mem -gt $memPico) { $memPico = $mem }
        $cpuSuma += $cpu; $n++
    }
}
$cpuProm = if ($n -gt 0) { $cpuSuma / $n } else { 0 }

# --- Registro --------------------------------------------------------------------------------
$csv = Join-Path $raiz "benchmark\resultados.csv"
$fila = [pscustomobject]@{
    motor        = $r.motor
    config       = $Config
    repeticion   = $Repeticion
    replicas     = $Replicas
    workers      = $r.workers
    nucleos      = $r.nucleos
    segundos     = $r.segundos
    arranque_s   = $r.arranque_s
    filas        = $r.filas
    mem_pico_mib = [math]::Round($memPico, 1)
    cpu_prom_pct = [math]::Round($cpuProm, 1)
    muestras     = $n
    top1         = $r.top1
    top1_n       = $r.top1_n
    fecha        = (Get-Date).ToString("s")
}
$cultura = [Threading.Thread]::CurrentThread.CurrentCulture
[Threading.Thread]::CurrentThread.CurrentCulture = [Globalization.CultureInfo]::InvariantCulture
$fila | Export-Csv $csv -Append -NoTypeInformation -Encoding UTF8
[Threading.Thread]::CurrentThread.CurrentCulture = $cultura

Write-Host ("{0} config {1} x{8} rep {2}: {3} s de cálculo, {4} s de arranque, pico {5} MiB, CPU {6} %, {7} filas" -f `
    $r.motor, $Config, $Repeticion, $r.segundos, $r.arranque_s, $fila.mem_pico_mib, $fila.cpu_prom_pct, $r.filas, $Replicas)
