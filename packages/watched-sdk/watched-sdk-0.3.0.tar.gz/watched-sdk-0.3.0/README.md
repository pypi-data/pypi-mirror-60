# WATCHED.com Python SDK

Python SDK to create addons for WATCHED.com.

You can find our overall documentation at https://git.blvck.dev/watched/docs

## Example addon

There are two ways to run the example addon.

### Just install it

```bash
# Install the watched_sdk
python setup.py install
# Start the addon
python example/main.py start
```

### Docker

```bash
# Build the container
docker build . -t watched-sdk-example
# Start it
docker run --rm -p 3000:3000 watched-sdk-example
# To run single commands:
docker run --rm -p 3000:3000 watched-sdk-example python example/main.py call
# To develop on the addon, use this:
docker run --rm -p 3000:3000 -v $PWD:/code watched-sdk-example python example/main.py start debug
```
