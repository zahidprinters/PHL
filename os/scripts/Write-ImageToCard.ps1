# Write the prepared odroid Debian .img to the USB card reader.
# Run from an ELEVATED PowerShell (right-click > Run as Administrator).
# Safety: refuses anything that is not the USB card; requires typing the disk number.
param(
    # Default is the eMMC backup image (the recovery use-case). Decompress
    # backup-eMMC\emmc_backup.img.gz -> .img first. Override with -Image.
    [string]$Image = 'd:\phl\os\backup-eMMC\emmc_backup.img',
    [int]$DiskNumber = 1,
    [string]$ConfirmDisk
)
$ErrorActionPreference = 'Stop'
if ($ConfirmDisk -ne '1') {
    throw "Safety: no confirmation. Re-run with:  -ConfirmDisk 1"
}
$img = Get-Item $Image
$disk = Get-Disk -Number $DiskNumber
Write-Host ("Target : Disk {0}  {1}  {2}  {3:N1} GB" -f $DiskNumber, $disk.FriendlyName, $disk.BusType, ($disk.Size/1GB))
if ($disk.BusType -ne 'USB') { throw "Refusing: disk $DiskNumber is $($disk.BusType), not USB." }
if ($disk.Size -lt $img.Length) { throw 'Refusing: image is larger than the card.' }
Write-Host ("Source : {0}  ({1:N0} bytes)" -f $img.Name, $img.Length)
$elev = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $elev) { throw 'Not elevated - run from an Administrator PowerShell.' }
# Staged write: each stage prints exactly where a failure occurs.
Write-Host 'Stage 1: image file readable...'
try {
    $probe = [System.IO.File]::OpenRead($img.FullName)
    $buf = New-Object byte[] (1MB)
    [void]$probe.Read($buf, 0, $buf.Length)
    $probe.Close()
    Write-Host '  OK (1 MB read)'
} catch { throw "Stage 1 image read FAILED: $($_.Exception.Message)" }

Write-Host 'Stage 2: erase partition table (frees the mounted volume - raw writes need no volume)...'
try {
    Clear-Disk -Number $DiskNumber -RemoveData -RemoveOEM -Confirm:$false
    Write-Host '  OK (Clear-Disk succeeded - disk is now empty and volume-free)'
} catch {
    Write-Host "  Clear-Disk failed: $($_.Exception.Message)"
    Write-Host '  -> if this says write-protected: hardware lock (slider/reader). Falling back to diskpart...'
    $tmp = Join-Path $env:TEMP 'dp_clean.txt'
    Set-Content -Path $tmp -Value ("select disk {0}`rclean`rexit" -f $DiskNumber) -Encoding Ascii
    & diskpart /s $tmp | Out-Null
    $dpCode = $LASTEXITCODE
    Remove-Item $tmp -ErrorAction SilentlyContinue
    if ($dpCode -ne 0) { throw "Stage 2 FAILED: diskpart clean also failed (exit $dpCode) - hardware write-protect suspected." }
    Write-Host '  OK (diskpart clean succeeded)'
}

Write-Host 'Stage 3: open disk for write...'
$ds = $null
for ($attempt = 1; $attempt -le 6; $attempt++) {
    try {
        $ds = New-Object System.IO.FileStream("\\.\PhysicalDrive$DiskNumber", [System.IO.FileMode]::Open, [System.IO.FileAccess]::Write, [System.IO.FileShare]::None, 1MB)
        break
    } catch {
        if ($attempt -eq 6) {
            Write-Host "  Open FAILED after 6 tries: $($_.Exception.Message)"
            Write-Host '  => close Disk Management (diskmgmt.msc), Explorer windows on the card,'
            Write-Host '     and any disk tools - they hold the raw disk open. Then re-run.'
            throw
        }
        Write-Host "  attempt $attempt busy ($($_.Exception.Message.Split(',')[0])) - retrying in 2s..."
        Start-Sleep -Seconds 2
    }
}
Write-Host '  OK'

Write-Host 'Stage 4: copying 4 GB to disk...'
$fs = $null
try {
    $fs = [System.IO.File]::OpenRead($img.FullName)
    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    $fs.CopyTo($ds)
    $ds.Flush($true); $ds.Close(); $ds = $null
    $fs.Close(); $fs = $null
    $sw.Stop()
    Write-Host ("  OK: {0:N0} bytes in {1:N0}s ({2:N1} MB/s)" -f $img.Length, $sw.Elapsed.TotalSeconds, ($img.Length/1MB/$sw.Elapsed.TotalSeconds))
} catch {
    Write-Host "  Copy FAILED: $($_.Exception.Message)"
    Write-Host '  => write-protected? check the adapter lock slider. Busy? close Explorer windows on E:.'
    throw
} finally {
    if ($ds) { $ds.Close() }
    if ($fs) { $fs.Close() }
}
Write-Host 'Partition table after write (no letters: ext4/btrfs are invisible to Windows - normal):'
Get-Partition -DiskNumber $DiskNumber -ErrorAction SilentlyContinue | Format-Table PartitionNumber, DriveLetter, Type, @{n='GB';e={[math]::Round($_.Size/1GB,1)}} -AutoSize
Write-Host 'Eject the card and move the board jumper to SD.'
