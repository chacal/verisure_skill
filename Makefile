include secrets.properties
export

build:
	@sam build

package: build
	@sam package --s3-bucket verisure-skill --output-template-file packaged_template.yaml

deploy: package
	@sam deploy --template-file packaged_template.yaml --stack-name verisure-skill --region us-east-1 --capabilities CAPABILITY_IAM --parameter-overrides $$(cat secrets.properties)

test_discovery: build
	@cat test_requests/discovery.json | sam local invoke | jq

test_lock: build
	@cat test_requests/lock.json | sam local invoke | jq

test_state: build
	@cat test_requests/report_state.json | sam local invoke | jq