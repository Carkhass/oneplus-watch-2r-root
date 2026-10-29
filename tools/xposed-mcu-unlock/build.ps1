# Compile le module Xposed « MCU Unlock » sans Gradle : javac -> d8 -> aapt2 -> sign.
# Prérequis : Android SDK (build-tools 35, platform android-34) + JDK 21. Adapter les chemins.
$ErrorActionPreference = 'Continue'
$root = $PSScriptRoot
$sdk  = "$env:LOCALAPPDATA\Android\Sdk"
$bt   = "$sdk\build-tools\35.0.0"
$jar  = "$sdk\platforms\android-34\android.jar"
$keytool = 'C:\Program Files\Java\jdk-21\bin\keytool.exe'
$javac   = 'C:\Program Files\Java\jdk-21\bin\javac.exe'
$pkgDir  = 'com\example\mcuunlock'   # <-- adapter si vous changez le package
$out  = "$root\build"; $cls = "$out\classes"
Remove-Item $out -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force $cls | Out-Null

Write-Host '// 1. javac (stubs Xposed compile-only + hook)'
$srcs = Get-ChildItem -Recurse "$root\src\*.java" | ForEach-Object { $_.FullName }
& $javac -source 17 -target 17 -cp $jar -d $cls $srcs
if ($LASTEXITCODE) { throw 'javac echoue' }

Write-Host '// 2. d8 (UNIQUEMENT le package du module, pas les stubs Xposed)'
$modClasses = Get-ChildItem -Recurse "$cls\$pkgDir\*.class" | ForEach-Object { $_.FullName }
& "$bt\d8.bat" --min-api 33 --output $out $modClasses
if ($LASTEXITCODE) { throw 'd8 echoue' }

Write-Host '// 3. aapt2 link (manifest seul)'
& "$bt\aapt2.exe" link -o "$out\base.apk" -I $jar --manifest "$root\AndroidManifest.xml"
if ($LASTEXITCODE) { throw 'aapt2 echoue' }

Write-Host '// 4. injecter classes.dex + assets/xposed_init (chemins forward-slash)'
Add-Type -A System.IO.Compression.FileSystem
$zip = [IO.Compression.ZipFile]::Open("$out\base.apk", 'Update')
foreach ($pair in @(@('classes.dex', "$out\classes.dex"), @('assets/xposed_init', "$root\assets\xposed_init"))) {
    $e = $zip.CreateEntry($pair[0], [IO.Compression.CompressionLevel]::Optimal)
    $s = $e.Open(); $by = [IO.File]::ReadAllBytes($pair[1]); $s.Write($by, 0, $by.Length); $s.Close()
}
$zip.Dispose()

Write-Host '// 5. align + sign'
& "$bt\zipalign.exe" -f -p 4 "$out\base.apk" "$out\aligned.apk"
if ($LASTEXITCODE) { throw 'zipalign echoue' }
$ks = "$out\debug.keystore"
if (-not (Test-Path $ks)) {
    & $keytool -genkeypair -keystore $ks -storepass android -keypass android -alias debug `
        -keyalg RSA -keysize 2048 -validity 10000 -dname 'CN=MCU Unlock' 2>&1 | Out-Null
}
& "$bt\apksigner.bat" sign --ks $ks --ks-pass pass:android --key-pass pass:android --out "$out\mcu-unlock.apk" "$out\aligned.apk"
if ($LASTEXITCODE) { throw 'signature echoue' }
Write-Host "OK -> $out\mcu-unlock.apk"
