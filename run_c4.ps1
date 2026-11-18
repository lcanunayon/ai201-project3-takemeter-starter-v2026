# Milestone 5, C4: clean checkout. For one trial, make a new empty folder and
# run the six lines of RUNNING.md "Clean-checkout setup" in a fresh PowerShell
# process, with no execution-policy override (the machine's real policy applies).
#
#   powershell -File run_c4.ps1 t1     # then t2, t3
#
# Output: logs/trials/c4_<trial>_out.txt, and a copy of the clone's log + meta.

param([Parameter(Mandatory)][string]$K)
$repo = $PSScriptRoot
$base = Join-Path $env:TEMP "takemeter_c4"
$dir = Join-Path $base "clonetest_$K"
if (Test-Path $dir) { Remove-Item -Recurse -Force $dir }
New-Item -ItemType Directory -Force $dir | Out-Null

# The six lines, verbatim from RUNNING.md (Windows variant of line 4).
$six = @'
git clone https://github.com/lcanunayon/ai201-project3-takemeter-starter-v2026.git
cd ai201-project3-takemeter-starter-v2026
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python classify.py classify "Canelo has been ducking Benavidez for years"
'@
$cmd = ($six -split "`r?`n" | Where-Object { $_ }) -join "`n"
$cmd += "`n" + 'exit $LASTEXITCODE'

# Don't inherit this session's Process-scope Bypass.
Remove-Item Env:PSExecutionPolicyPreference -ErrorAction SilentlyContinue
$out = Join-Path $repo "logs\trials\c4_${K}_out.txt"
$t = [Diagnostics.Stopwatch]::StartNew()
Push-Location $dir
& powershell.exe -Command $cmd *> $out
$code = $LASTEXITCODE
Pop-Location
$secs = [math]::Round($t.Elapsed.TotalSeconds, 1)

$clone = Join-Path $dir "ai201-project3-takemeter-starter-v2026"
$log = Join-Path $clone "logs\classify_log.jsonl"
$meta = Join-Path $clone "models\takemeter\takemeter_meta.json"
Copy-Item $log (Join-Path $repo "logs\trials\c4_${K}_clone_log.jsonl") -ErrorAction SilentlyContinue
Copy-Item $meta (Join-Path $repo "logs\trials\c4_${K}_meta.json") -ErrorAction SilentlyContinue
$lines = if (Test-Path $log) { @(Get-Content $log) } else { @() }
$summary = @"

=== C4 $K summary ===
folder: $dir
exit code of last line: $code
seconds, all six lines: $secs
log lines in clone: $($lines.Count)
last log line status: $(if ($lines) { ($lines[-1] | ConvertFrom-Json).status } else { 'none' })
test_accuracy: $(if (Test-Path $meta) { (Get-Content $meta -Raw | ConvertFrom-Json).test_accuracy } else { 'no meta' })
"@
Add-Content -Path $out -Value $summary -Encoding utf8
$summary
