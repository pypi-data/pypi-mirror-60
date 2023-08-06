import functools
import sys
import time


def backoff(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        for i in range(5):
            try:
                return fn(*args, **kwargs)
            except Exception:
                sys.stderr.write(f"Exceeded limit in {fn.__name__}, sleeping {i+1}\n")
                time.sleep(i+1)

        raise Exception(f"Ran out of retries for {fn.__name__}")

    return wrapper

@backoff
def tags_for_stream(client, stream):
    r = client.list_tags_for_stream(StreamName=stream)
    return {el['Key']: el['Value'] for el in r['Tags']}


@backoff
def fetch_streams(client, last=None):
    if last:
        return client.list_streams(Limit=500, ExclusiveStartStreamName=last)
    else:
        return client.list_streams(Limit=500)


def streams(client):
    last = None
    while True:
        r = fetch_streams(client, last)
        for s in r['StreamNames']:
            yield s
            last = s

        if not r['HasMoreStreams']:
            break

