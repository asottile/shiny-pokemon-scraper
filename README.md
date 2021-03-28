[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/asottile/shiny-pokemon-scraper/master.svg)](https://results.pre-commit.ci/latest/github/asottile/shiny-pokemon-scraper/master)

shiny-pokemon-scraper
=====================

automatically detect max raid events with guaranteed shiny pokemon

I always seem to miss the max raid battle events (which sometimes have
guaranteed shiny pokemon!).  I decided to try and automate this using a
reputable news source and a little bit of code.

this code does the following:

- load [any event den page]
- find the latest event den
- if the latest event den has `<b>Shiny Rate</b>` send an email.  for example
  [the flower event]
- (state is retained so it only emails once)

[any event den page]: https://serebii.net/swordshield/maxraidbattles/eventden-may2020.shtml
[the flower event]: https://www.serebii.net/swordshield/maxraidbattles/eventden-flowerevent.shtml

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
