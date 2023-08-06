# `nouns`: Data-deterministic, structure-driven (very experimental) templating

`nouns` does templating a bit differently - the templating itself is quite primitive, with most of the gruntwork taking place in the preprocessing layer.

This layer converts all the templating data into a very general form that ensures the data is renderable by the templates no matter the structure of the data.

## Hello world

Do traditional template-and-data templating as follows:

    >>> from nouns import template
    >>> template(dict(name='World'), 'Hello $name!')
    Hello World!

But the more interesting/intended use is to not explicitly pass in a template. Instead, just pass in the data - let the templating engine itself figure out which templates to use.

The in-built templates are designed to give you something close to what you probably want.

Pass in a table of data, you'll get a table back. Pass in a dictionary/mapping, you'll get the key/value pairs templated in a table. Pass in a list, you'll get each list item templated out.

## Experimental status

This templating system is an experiment in how to craft the most data-driven templating system, where the output is dependent on the things ("nouns") you pass in.

We will initially use if for rendering data in notebooks, but it's definitely not production-ready for web applications or otherwise rendering untrusted data, without a lot of extra customization and filters set up.

Hopefully it will continue to evolve toward production-ready status.