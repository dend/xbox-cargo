# xbox-cargo

A command-line tool designed to help you manage your Xbox Live content. It started from my aspiration to [back up my Xbox Live media content](https://den.dev/blog/xbox-live-download-captures/) locally without involving OneDrive or relying on one-by-one media selection through the app.

## Usage

```bash
positional arguments:
  {download,clean}
    download        Download media from the Xbox network.
    clean           Clean media from an Xbox network account.

optional arguments:
  -h, --help        show this help message and exit
```

### Downloading Media

```bash
usage: __main__.py download [-h] [--token token] [--download-location dl] [--xuid xuid] [--media {s,v,a}]

optional arguments:
  -h, --help            show this help message and exit
  --token token         XBL 3.0 authorization token.
  --download-location dl
                        Folder where content needs to be downloaded.
  --xuid xuid           Xbox Live numeric user identifier.
  --media {s,v,a}       Type of media to be downloaded. Use S for screenshots, V, for video, or A for all.
```

Because the application is written in Python, you can invoke it from the terminal through the Python interpreter:

```python
python -m xc download --token YOUR_TOKEN --download-location ~/LOCAL/FOLDER --xuid YOUR_XUID --media MEDIA_MODE
```

In the example above, `MEDIA_MODE` can be `s` (for screenshots), `v` for videos, or `a` for all.

### Cleaning Media

```bash
usage: __main__.py clean [-h] [--mode {all,select}] [--token token] [--xuid xuid]

optional arguments:
  -h, --help           show this help message and exit
  --mode {all,select}  Determines the mode of cleanup to be performed.
  --token token        XBL 3.0 authorization token.
  --xuid xuid          Xbox Live numeric user identifier. Optional for selective cleanup.
```

Removing media from the Xbox network is similar to downloading - use the Python interpreter to launch the application:

```python
python -m xc clean --token YOUR_TOKEN --xuid YOUR_XUID --mode CLEANUP_MODE
```

Currently, only the `all` mode is implemented.
