venv:
	source .venv/bin/activate

clean:
	cdk context --clear

synth:
	cdk synth --all

diff:
	cdk diff --all

bootstrap:
	cdk bootstrap

deploy:
	cdk deploy ValheimAws --require-approval never

destroy:
	cdk destroy --all --require-approval never

upload:
	aws s3 cp ./s3_files s3://valheim-aws/ --recursive

download:
	aws s3 cp s3://valheim-aws/ ./s3_files --recursive
