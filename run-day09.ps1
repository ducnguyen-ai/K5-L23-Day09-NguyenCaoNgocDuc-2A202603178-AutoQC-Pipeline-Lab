param([ValidateSet('test','calibrate','run','check-core','check')][string]$Action='test')
$ErrorActionPreference='Stop'
# Linux avoids the instructor checker's Windows path and CRLF hash differences.
$drive=$PSScriptRoot.Substring(0,1).ToLower()
$linuxRepo='/mnt/'+$drive+$PSScriptRoot.Substring(2).Replace('\','/')
$python='/root/.venvs/day09-qc/bin/python'
switch($Action) {
 'test' {$commandArgs=@('-m','pytest','-q')}
 'calibrate' {$commandArgs=@('-m','pipeline.calibrate','--sweep','duplicates.phash_dist=2,4,6,8,10,12,14,16,20','--sweep','second_opinion.conf=0.1,0.25,0.4,0.5,0.6,0.7,0.8','--out','submission/calibration')}
 'run' {$commandArgs=@('-m','pipeline.run')}
 'check-core' {$commandArgs=@('scripts/check_submission.py','--no-train')}
 'check' {$commandArgs=@('scripts/check_submission.py')}
}
& wsl -d Ubuntu -u root --cd $linuxRepo -- $python @commandArgs
exit $LASTEXITCODE
