[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/asottile/shiny-pokemon-scraper/main.svg)](https://results.pre-commit.ci/latest/github/asottile/shiny-pokemon-scraper/main)

shiny-pokemon-scraper
=====================

automatically detect tera raid events with guaranteed shiny pokemon

I always seem to miss the tera raid battle events (which sometimes have
guaranteed shiny pokemon!).  I decided to try and automate this using a
reputable news source and a little bit of code.

this code does the following:

- load [any event den page]
- find the latest event den
- if the latest event den has `<b>Shiny Rate</b>` send an email.  for example
  [the charizard event]
- (state is retained so it only emails once)

[any event den page]: https://www.serebii.net/scarletviolet/teraraidbattles/event-eeveespotlight.shtml
[the charizard event]: https://www.serebii.net/scarletviolet/teraraidbattles/event-unrivaledcharizard.shtml

### architecture

```
  +=====================+   (cron trigger)   +=====================+
  |  cloudwatch events  |------------------->| lambda (handler.py) |
  +=====================+                    +=====================+
                                             |      |       ^
                      +===============+<-----+      +-------+
                      |  SES (email)  |         self-modifying (state.txt)
                      +===============+
```

### setup

before setting up, you'll need SES sending enabled.  I had this configured
from another terraform module so that's left out of the terraform here

```bash
cd terraform
terraform init
terraform apply --var email_from=... --var email_to=...
cd ..
```

after the infrastructure is set up, you'll need to deploy the lambda

```bash
zip out.zip handler.py
aws lambda update-function-code --function-name mrb_scraper --zip-file fileb://out.zip
```

testing the lambda

```bash
aws lambda invoke --function-name mrb_scraper --log-type=Tail /dev/stdout |
    jq --raw-output .LogResult |
    base64 -d
```
