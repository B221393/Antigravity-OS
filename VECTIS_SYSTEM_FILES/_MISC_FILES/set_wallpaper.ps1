Param(
    [Parameter(Mandatory = $true)]
    [string]$WallpaperPath
)

$code = @"
using System.Runtime.InteropServices;
public class Wallpaper {
    [DllImport("user32.dll", CharSet = CharSet.Auto)]
    public static extern int SystemParametersInfo(int uAction, int uParam, string lpvParam, int fuWinIni);
}
"@

Add-Type -TypeDefinition $code
$fullPath = Resolve-Path $WallpaperPath
[Wallpaper]::SystemParametersInfo(20, 0, $fullPath.Path, 3)

Write-Output "Wallpaper set to: $($fullPath.Path)"
