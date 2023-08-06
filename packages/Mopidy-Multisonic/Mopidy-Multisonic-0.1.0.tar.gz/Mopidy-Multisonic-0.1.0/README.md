Mopidy Multisonic
=================

Yes, another mopidy subsonic backend provider. This module allow multiple
subsonic server providers

## Installation

Install by running::

```
python3 -m pip install Mopidy-Subsonic
```

## Configuration

Before starting Mopidy, you must add configuration for
Mopidy-Subsonic to your Mopidy configuration file::

```
[multisonic]
providers = PROVIDER_NAME:PROTOCOL:TARGET:USERNAME:PASSWORD[,ANOTHER?]
```

```
[multisonic]
providers = banalisation:https:music.banalserver.com:mr_banal:azerty
```

```
[multisonic]
providers = banalisation:https:music.banalserver.com:mr_banal:azerty,decadence:http:toot.com:h4ck3r:1213
```


Project resources
=================

- [Source code](https://hg.sr.ht/~reedwade/mopidy_multisonic)
- [Todo code](https://todo.sr.ht/~reedwade/Mopidy-Multisonic)
- [Mailing list](https://lists.sr.ht/~reedwade/mopidy_multisonic)
- [Changelog](https://hg.sr.ht/~reedwade/mopidy_multisonic/browse/default/CHANGELOG.rst)


Credits
=======

- Original author: [ReedWade](https://hg.sr.ht/~reedwade)
- Current maintainer: [ReedWade](https://hg.sr.ht/~reedwade)
- [Contributors](https://hg.sr.ht/~reedwade/mopidy_multisonic/contributors)
