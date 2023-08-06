Mopidy Multisonic
=================

Yes, another mopidy subsonic backend provider. This module allow multiple
subsonic server providers

## Installation

Install by running::

    python3 -m pip install Mopidy-Multisonic

## Configuration

Before starting Mopidy, you must add configuration for
Mopidy-Multisonic to your Mopidy configuration file::

	[multisonic]
	providers =
	  PROVIDER_NAME: PROTOCOL://USERNAME:PASSWORD@TARGET
	  [ANOTHER]

	[multisonic]
	providers =
	  banalisation: https://mr_banal:azerty@music.banalserver.com

	[multisonic]
	providers =
	  banalisation: https://mr_banal:azerty@music.banalserver.com
	  decadence: http://h4ck3r:1213@toot.com


Project resources
=================

- `Source code <https://hg.sr.ht/~reedwade/mopidy_multisonic>`_
- `Todo code <https://todo.sr.ht/~reedwade/Mopidy-Multisonic>`_
- `Mailing list <https://lists.sr.ht/~reedwade/mopidy_multisonic>`_
- `Changelog <https://hg.sr.ht/~reedwade/mopidy_multisonic/browse/default/CHANGELOG.rst>`_


Credits
=======

- Original author: `ReedWade <https://hg.sr.ht/~reedwade>`__
- Current maintainer: `ReedWade <https://hg.sr.ht/~reedwade>`__
- `Contributors <https://hg.sr.ht/~reedwade/mopidy_multisonic/contributors>`_
