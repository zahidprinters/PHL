# Hash the card's image-sized region and compare against the prepared image.
# READ-ONLY. Run ELEVATED:  powershell -ExecutionPolicy Bypass -File Compare-Card.ps1
$ErrorActionPreference = 'Stop'
$d = Get-Disk -Number 1
if ($d.BusType -ne 'USB') { throw 'Disk 1 is not a USB disk - is the card reader attached?' }
"card disk: Disk 1  $($d.FriendlyName)  $([math]::Round($d.Size/1GB,1)) GB"
# Default is the eMMC backup image (the recovery verification case).
# Decompress backup-eMMC\emmc_backup.img.gz -> .img first. Override the path below.
$imgPath = 'd:\phl\os\backup-eMMC\emmc_backup.img'
$need = [int64](Get-Item $imgPath).Length
"hashing $need bytes from card and image - takes 1-3 minutes..."
$h = [System.Security.Cryptography.SHA256]::Create()
$fs = [System.IO.File]::OpenRead('\\.\PhysicalDrive1')
$buf = New-Object byte[] (4194304)
$total = [int64]0
while ($total -lt $need) {
    $chunk = [int][Math]::Min([int64]$buf.Length, ($need - $total))
    $n = $fs.Read($buf, 0, $chunk)
    if ($n -le 0) { break }
    [void]$h.TransformBlock($buf, 0, $n, $null, 0)
    $total += $n
}
$fs.Close()
[void]$h.TransformFinalBlock($buf, 0, 0)
$card = ([BitConverter]::ToString($h.Hash) -replace '-','').ToLower()
$img  = (Get-FileHash $imgPath -Algorithm SHA256).Hash.ToLower()
"card : $card   ($total bytes read)"
"image: $img   ($need bytes)"
if ($card -eq $img -and $total -eq $need) {
    'MATCH - card is byte-identical to the prepared image'
} else {
    'MISMATCH - card content differs from the prepared image'
}
