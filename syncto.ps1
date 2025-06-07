# syncto.ps1

# 1. Ruta a los repos
$origin = "." 
$dest   = "..\perfilizer"

# 2. Cambiar a rama perfilizer
Set-Location $origin
git checkout perfilizer
git pull

# 3. Copiar archivos (sin .git)
robocopy $origin $dest /MIR /XD ".git" /NFL /NDL /NJH /NJS /NC /NS /NP

# Confirmar en consola
Write-Host "-OK- Archivos sincronizados con /MIR (mirror exacto)"

# 4. Subir cambios
Set-Location $dest
git add .
git commit -m "Sincronización desde prj-go"
git push

#5. Volver a la rama de trabajo
.\comeback.ps1


