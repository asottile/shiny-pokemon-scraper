from __future__ import annotations

import contextlib
import email.message
import html.parser
import io
import os.path
import urllib.request
import zipfile

import boto3

lambda_client = boto3.client('lambda')
ses_client = boto3.client('ses')

URL = 'https://serebii.net/swordshield/maxraidbattles/eventden-may2020.shtml'
EMAIL_FROM = os.environ['EMAIL_FROM']
EMAIL_TO = os.environ['EMAIL_TO']


class FindSelect(html.parser.HTMLParser):
    def __init__(self) -> None:
        super().__init__()

        self.page: str | None = None
        self._in_select = False

    def handle_starttag(
            self,
            tag: str,
            attrs: list[tuple[str, str | None]],
    ) -> None:
        attrs_d = dict(attrs)
        if (
                not self._in_select and
                tag == 'select' and
                attrs_d['name'] == 'SelectURL'
        ):
            self._in_select = True
        elif self._in_select and self.page is None and attrs_d:
            self.page = f'https://serebii.net{attrs_d["value"]}'


def lambda_handler(event: object, context: object) -> None:
    try:
        with open('state.txt') as f:
            prev = f.read().strip()
    except FileNotFoundError:
        prev = ''
    print(f'previous url: {prev}')

    resp = urllib.request.urlopen(URL)
    parser = FindSelect()
    parser.feed(resp.read().decode(errors='ignore'))
    assert parser.page is not None
    print(f'current url: {parser.page}')

    if prev == parser.page:
        print('already up to date!')
        return

    resp = urllib.request.urlopen(parser.page)
    if b'<b>Shiny Rate</b>' in resp.read():
        print('SHINY!')

        msg = email.message.EmailMessage()
        msg['Subject'] = 'NEW SHINY RAID!'
        msg['From'] = EMAIL_FROM
        msg['To'] = EMAIL_TO
        msg.set_content(
            f'CHECK OUT THIS HOT NEW MAX RAID BATTLE\n\n'
            f'IT HAS A SHINY\n\n'
            f'{parser.page}',
        )

        ses_client.send_raw_email(
            Source=msg['From'],
            Destinations=[msg['To']],
            RawMessage={'Data': msg.as_string()},
        )
    else:
        print('not shiny')

    with contextlib.suppress(OSError):  # lambda is a readonly filesystem
        with open('state.txt', 'w') as f:
            f.write(f'{parser.page}\n')

    bio = io.BytesIO()
    with zipfile.ZipFile(bio, 'w') as zipf:
        zipf.write(os.path.basename(__file__))

        info = zipfile.ZipInfo('state.txt')
        info.external_attr = 0o644 << 16
        zipf.writestr(info, f'{parser.page}\n')

    lambda_client.update_function_code(
        FunctionName='mrb_scraper',
        ZipFile=bio.getvalue(),
    )


def main() -> int:
    lambda_handler(None, None)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
