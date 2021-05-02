@echo off
set local_path=folder01
set bucket_name=private-igapon
if "%1"=="" (
aws s3 sync %local_path% s3://%bucket_name%/
) else (
aws s3 sync %local_path% s3://%1/
)
