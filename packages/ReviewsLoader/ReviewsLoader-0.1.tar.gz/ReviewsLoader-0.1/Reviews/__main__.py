import click
import asyncio

from .ReviewsLoader import ReviewsLoader
from .CSVReviewsWriter import CSVRewiewsWriter
from .DefaultDataConverter import DefaultDataConverter


# Current token expires in June
DEFAULT_TOKEN = "eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IldlYlBsYXlLaWQifQ.eyJpc3MiOiJBTVBXZWJQbGF5IiwiaWF0IjoxNTc5NjM3MzI0LCJleHAiOjE1OTUxODkzMjR9.SCgFvMtDJmpfGBYGjJ9ss9aloYssX7HYq0eI-xyQssNruaVLI_wXLWPDUtigBXDQrwVCPariPfcvOLvEn067lg"


PARSERS = {
    'default': DefaultDataConverter
}


WRITERS = {
    'csv': CSVRewiewsWriter
}


async def run(loop, app_id, batch_size, requests_interval, output, format, parser, token):
    loader = ReviewsLoader(loop, app_id, token)
    writer = WRITERS[format](output, PARSERS[parser].get_fieldnames())
    async for review in loader.get(batch_size=batch_size, requests_interval=requests_interval):
        await writer.write(PARSERS[parser].convert(review))


@click.command()
@click.argument('app_id', required=True, type=str)
@click.option('--batch_size', default=2000, show_default=True, type=int, help='One-time download batch size.')
@click.option('--requests_interval', default=0.3, show_default=True, type=float, help='Batch request interval.')
@click.option('--output', default='reviews.csv', show_default=True, type=str, help='Output file name.')
@click.option('--format', default='csv', show_default=True, type=str, help='Output file format.')
@click.option('--parser', default='default', show_default=True, type=str, help='Data parser.')
@click.option('--token', type=str, help='Authorization token.')
def main(app_id, batch_size, requests_interval, output, format, parser, token=None):
    """Utility for downloading app reviews in the App Store."""
    if token is None:
        token = DEFAULT_TOKEN
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(loop, app_id, batch_size, requests_interval, output, format, parser, token))
    loop.close()

if __name__ == '__main__':
    main()
