param([ValidateSet('test','calibrate','run','check-core','check','train')][string]$Action='test')
$ErrorActionPreference='Stop'
# Linux avoids the instructor checker's Windows path and CRLF hash differences.
$drive=$PSScriptRoot.Substring(0,1).ToLower()
$linuxRepo='/mnt/'+$drive+$PSScriptRoot.Substring(2).Replace('\','/')
$python='/root/.venvs/day09-qc/bin/python'
if($Action -eq 'train') {
    $env:PYTHONUTF8='1'
    $env:YOLO_CONFIG_DIR=Join-Path $PSScriptRoot 'work/setup/ultralytics_config'
    $gpuPython=Join-Path $PSScriptRoot '.venv-train/Scripts/python.exe'
    Push-Location $PSScriptRoot
    try {
        & $gpuPython -c "from ultralytics import settings; settings.update({k:False for k in ['sync','wandb','comet','mlflow','clearml','tensorboard','dvc','neptune'] if k in settings})"
        if($LASTEXITCODE -ne 0){exit $LASTEXITCODE}
        & $gpuPython scripts/train_compare.py --variants raw clean --seeds 0 1 --epochs 20 --batch 16 --imgsz 640 --device 0 --skip-existing
        $trainCode=$LASTEXITCODE
        if($trainCode -eq 0){& $gpuPython scripts/summarize_results.py; $trainCode=$LASTEXITCODE}
    } finally {Pop-Location}
    exit $trainCode
}
switch($Action) {
 'test' {$commandArgs=@('-m','pytest','-q')}
 'calibrate' {$commandArgs=@('-m','pipeline.calibrate','--sweep','duplicates.phash_dist=2,4,6,8,10,12,14,16,20','--sweep','second_opinion.conf=0.1,0.25,0.4,0.5,0.6,0.7,0.8','--out','submission/calibration')}
 'run' {$commandArgs=@('-m','pipeline.run')}
 'check-core' {$commandArgs=@('scripts/check_submission.py','--no-train')}
 'check' {$commandArgs=@('scripts/check_submission.py')}
}
& wsl -d Ubuntu -u root --cd $linuxRepo -- $python @commandArgs
exit $LASTEXITCODE
