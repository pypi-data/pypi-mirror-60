
Crickly-playcricket 🏏
==================================

Crickly-PlayCricket is an extension to [Crickly](https://github.com/Crickly/crickly/). It links the core app with the ECB Play Cricket System.

📝 _Note_: Development is still in progress and not in a stable state. I doubt it'll (know it wont) work yet! 🤪

Detailed documentation is in the "docs" directory. (Not produced yet. So instead heres a unicorn... 🦄)


Quick start 🛫
-------------
To use this app you will need an API Token provided by the [Play Cricket Helpdesk](https://play-cricket.ecb.co.uk/hc/en-us/requests/new?ticket_form_id=217809).


1. Add `cricket.core` and `cricket.playcricket` to your INSTALLED_APPS setting like this

```
    INSTALLED_APPS = [
        ...
        'cricket.core',
        'cricket.playcricket',
    ]
```

2. Run `python manage.py migrate` to create the cricket models.
