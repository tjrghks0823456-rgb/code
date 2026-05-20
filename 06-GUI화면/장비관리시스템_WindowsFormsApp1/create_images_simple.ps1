
# Define the output directory
$outDir = "c:\Users\User\Documents\카카오톡 받은 파일\WindowsFormsApp1 (2)\bin\Debug\Images"
if (-not (Test-Path $outDir)) {
    New-Item -ItemType Directory -Path $outDir -Force
}

Add-Type -AssemblyName System.Drawing

# Function to save colored image
function Save-ColorImage {
    param($Name, $ColorName)
    try {
        $path = Join-Path $outDir $Name
        $bmp = New-Object System.Drawing.Bitmap 200, 200
        $g = [System.Drawing.Graphics]::FromImage($bmp)
        $c = [System.Drawing.Color]::FromName($ColorName)
        $brush = New-Object System.Drawing.SolidBrush $c
        $g.FillRectangle($brush, 0, 0, 200, 200)
        
        $bmp.Save($path, [System.Drawing.Imaging.ImageFormat]::Png)
        Write-Host "Created $Name"
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
