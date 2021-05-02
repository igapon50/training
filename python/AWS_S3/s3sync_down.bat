@echo off
set local_path=folder01
set bucket_name=private-igapon
if "%1"=="" (
aws s3 sync s3://%bucket_name%/ %local_path%
) else (
aws s3 sync s3://%1/ %local_path%
)
