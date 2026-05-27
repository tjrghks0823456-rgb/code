
# Valid relative path from the current working directory
$outDir = ".\bin\Debug\Images"

# Create directory if it doesn't exist
if (-not (Test-Path $outDir)) {
    New-Item -ItemType Directory -Path $outDir -Force | Out-Null
}

Add-Type -AssemblyName System.Drawing

# Function to save colored image
function Save-ColorImage {
    param($Name, $ColorName)
    try {
        # Use simple path combination ('.' is current dir)
        $path = "$outDir\$Name"
        
        # Ensure path is absolute for .NET calls to avoid ambiguity
        $absPath = Convert-Path $outDir
        $fullPath = Join-Path $absPath $Name

        $bmp = New-Object System.Drawing.Bitmap 200, 200
        $g = [System.Drawing.Graphics]::FromImage($bmp)
        $c = [System.Drawing.Color]::FromName($ColorName)
        $brush = New-Object System.Drawing.SolidBrush $c
        $g.FillRectangle($brush, 0, 0, 200, 200)
        
        $bmp.Save($fullPath, [System.Drawing.Imaging.ImageFormat]::Png)
        Write-Host "Created $fullPath"
    }
    catch {
        Write-Host "Failed to create $Name : $_"
    }
    finally {
        if ($g) { $g.Dispose() }
        if ($bmp) { $bmp.Dispose() }
        if ($brush) { $brush.Dispose() }
    }
}

Save-ColorImage "Cleaning.png" "LightBlue"
Save-ColorImage "Lithography.png" "LightYellow"
Save-ColorImage "Etching.png" "LightCoral"
Save-ColorImage "Deposition.png" "Silver"
Save-ColorImage "Furnace.png" "Orange"
Save-ColorImage "IonImplant.png" "LightGreen"
Save-ColorImage "CMP.png" "RosyBrown"
Save-ColorImage "Default.png" "White"
