# uploading

## saving the data on the playa

There are utility functions to save an event to the local file system.
Create an instance of `PurrsistantItem()` and call the `.save()` method.

```python
import logging

try:
    PurrsistantItem("00000000", "CAT Camp", "", ItemType.STAMP).save()
except PurrException as whoops:
    logging.exception(whoops)
```

The default save directory is `./purrsistant` - this is changable through
the public variable `PURRSISTANT_ROOT`.  Saved data has some restrictions:

- id_in must be a hex string of at least 8 chars from the SDK
- cn_in must match your registered camp/artwork name
- item_in must be "" or a base64 encoded value of less than 3 MiB in size that when decoded, is a JPEG or PNG file
- type_in is an enum, STAMP for a small achivement stamp or 'award', and PHOTO for a photo that should be shown in large form
- for each vistor, only one item is saved

There are some basic checks on save, with others validated at upload time.
