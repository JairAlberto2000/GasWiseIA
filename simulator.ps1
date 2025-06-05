# Parámetros de conexión
$host = "thegaswise.com"
$puerto = 5000
$usuario = "montse"
$clave = "123456"
$baseDatos = "DBGasWise"

# Datos base
$dispositivoID = 1
$magnitud = 0.0
$fechaBase = Get-Date

# Simular 10 días de consumo
for ($i = 0; $i -lt 10; $i++) {
    $lecturaID = 100 + $i           # Puedes ajustar esto según tus IDs reales
    $resultado = 44.15 - ($i * 0.8) # Disminuye cada vez (simula consumo)
    $fecha = $fechaBase.AddDays($i).ToString("yyyy-MM-dd HH:mm:ss")

    $query = "INSERT INTO Resultados_Lecturas (DispositivoID, LecturaID, magnitud, Resultado, Fecha) VALUES ($dispositivoID, $lecturaID, $magnitud, $resultado, '$fecha');"

    $comando = "mysql -h $host -P $puerto -u $usuario -p$clave $baseDatos -e `" $query `"" 
    Write-Host "Ejecutando inserción para día $i → Resultado: $resultado%"
    Invoke-Expression $comando
}
