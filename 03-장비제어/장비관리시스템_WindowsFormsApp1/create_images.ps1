
# Define the output directory
$outDir = "c:\Users\User\Documents\카카오톡 받은 파일\WindowsFormsApp1 (2)\bin\Debug\Images"
if (-not (Test-Path $outDir)) {
    New-Item -ItemType Directory -Path $outDir -Force
}

# Values: FileName, BackgroundColor, Text
$images = @(
    @{ Name="Cleaning.png"; Color="LightBlue"; Text="Cleaning (Wet Bench)" },
    @{ Name="Lithography.png"; Color="LightYellow"; Text="Lithography" },
    @{ Name="Etching.png"; Color="Red"; Text="Etching" },
    @{ Name="Deposition.png"; Color="LightGray"; Text="Deposition" },
    @{ Name="Furnace.png"; Color="Orange"; Text="Furnace" },
    @{ Name="IonImplant.png"; Color="Green"; Text="Ion Implant" },
    @{ Name="CMP.png"; Color="Brown"; Text="CMP" },
    @{ Name="Default.png"; Color="White"; Text="No Image" }
)

Add-Type -AssemblyName System.Drawing

foreach ($img in $images) {
    $bmp = New-Object System.Drawing.Bitmap 300, 300
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $g.Clear([System.Drawing.Color]::FromName($img.Color))
    
    $font = New-Object System.Drawing.Font "Arial", 20, [System.Drawing.FontStyle]::Bold
    $brush = [System.Drawing.Brushes]::Black
    $rect = New-Object System.Drawing.RectangleF 0, 0, 300, 300
    $format = New-Object System.Drawing.StringFormat
    $format.Alignment = [System.Drawing.StringAlignment]::Center
    $format.LineAlignment = [System.Drawing.StringAlignment]::Center
    
    $g.DrawString($img.Text, $font, $brush, $rect, $format)
    
    $path = Join-Path $outDir $img.Name
    $bmp.Save($path, [System.Drawing.Imaging.ImageFormat]::Png)
    
    $g.Dispose()
    $bmp.Dispose()
    Write-Host "Created $($img.Name)"
}
